import os
import shutil
import tempfile
import pandas as pd
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Response, Cookie, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from itsdangerous import Signer, BadSignature

from utils.analyzer import (
    extract_skills,
    analyze,
    match_score,
    get_job_roles,
    analyze_comprehensive
)
from utils.recommender import (
    get_recommendations,
    get_prioritized_recommendations,
    generate_strategic_advice
)
from utils.generator import generate_pdf, generate_skill_gap_report_pdf
from utils.parser import extract_text_from_pdf, extract_text_from_txt
from utils.db_helper import (
    register_user,
    verify_user_otp,
    generate_and_update_otp,
    authenticate_user,
    save_resume,
    load_resume,
    save_projects,
    load_projects,
    log_analysis,
    load_analysis_history,
    run_migrations
)
from utils.email_helper import send_verification_email

# Run migrations on startup
try:
    run_migrations()
except Exception as e:
    print(f"Startup migrations failed: {e}")

app = FastAPI(title="Elevora - Resume Skill Gap Analyzer & Career Intelligence API")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Secret key for signing session cookie
SECRET_KEY = "resume-analyzer-secure-key-1234!"
signer = Signer(SECRET_KEY)

# Ensure static directory exists (safe for read-only serverless filesystems)
try:
    os.makedirs(STATIC_DIR, exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
except Exception:
    pass

# Helper to get current user from signed cookie
def get_current_user(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        unsigned_data = signer.unsign(session_id.encode()).decode()
        user_id, username = unsigned_data.split(":")
        return {"id": int(user_id), "username": username}
    except (BadSignature, ValueError):
        raise HTTPException(status_code=401, detail="Invalid session")

# Pydantic schemas
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class VerifyRequest(BaseModel):
    username_or_email: str
    otp: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ProjectItem(BaseModel):
    title: str
    desc: str

class ResumeSaveRequest(BaseModel):
    name: str
    phone: str
    email: str
    location: str
    linkedin: str
    objective: str
    education: str
    languages: str
    database: str
    tools: str
    concepts: str
    achievements: str
    activities: str
    extra_curricular: str
    projects: List[ProjectItem]

class ResendOtpRequest(BaseModel):
    username_or_email: str

# AUTHENTICATION ENDPOINTS

@app.post("/api/auth/register")
def api_register(req: RegisterRequest):
    try:
        res = register_user(req.username, req.email, req.password)
        return {
            "success": True, 
            "message": "Account created and activated successfully! You can now sign in."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/resend-otp")
def api_resend_otp(req: ResendOtpRequest):
    try:
        res = generate_and_update_otp(req.username_or_email)
        if not res["success"]:
            raise HTTPException(status_code=400, detail=res["message"])
        
        # Send fresh verification code
        send_verification_email(res["email"], res["username"], res["otp"])
        return {
            "success": True,
            "message": f"A fresh verification code has been dispatched to {res['email']}."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/verify")
def api_verify(req: VerifyRequest):
    res = verify_user_otp(req.username_or_email, req.otp)
    if res["success"]:
        return {"success": True, "message": res["message"]}
    else:
        raise HTTPException(status_code=400, detail=res["message"])

@app.post("/api/auth/login")
def api_login(req: LoginRequest, response: Response):
    try:
        user = authenticate_user(req.username, req.password)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid username/email or password.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Sign session data: "user_id:username"
    session_data = f"{user['id']}:{user['username']}"
    signed_session = signer.sign(session_data.encode()).decode()
    
    # Set HTTP-only cookie
    response.set_cookie(
        key="session_id",
        value=signed_session,
        httponly=True,
        max_age=3600 * 24 * 7, # 7 days
        samesite="lax",
        secure=False # Set to True in production with HTTPS
    )
    return {"success": True, "username": user["username"]}

@app.post("/api/auth/logout")
def api_logout(response: Response):
    response.delete_cookie("session_id")
    return {"success": True, "message": "Logged out successfully"}

@app.get("/api/auth/me")
def api_me(current_user: dict = Depends(get_current_user)):
    return {"authenticated": True, "user": current_user}

# JOBS DATA ENDPOINT
@app.get("/api/jobs")
def api_get_jobs():
    try:
        roles = get_job_roles()
        return roles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load job roles: {str(e)}")

# SKILL GAP ANALYZER ENDPOINT (DATA SCIENCE & NLP POWERED)
@app.post("/api/analyze")
async def api_analyze(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_role: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    if not (job_description and job_description.strip()) and not (job_role and job_role.strip()):
        raise HTTPException(status_code=400, detail="Please provide a Job Description (JD) or select a Target Role.")

    # Extract text from uploaded resume file
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    # Save file temporarily in OS temp directory (never in project directory)
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, f"elevora_upload_{current_user['id']}_{os.getpid()}{file_ext}")
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        if file_ext == ".pdf":
            resume_text = extract_text_from_pdf(temp_file_path)
        elif file_ext == ".txt":
            with open(temp_file_path, "r", encoding="utf-8", errors="ignore") as f:
                resume_text = f.read()
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload .pdf or .txt")
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty or could not be parsed.")

    # 1. Run Comprehensive Multi-Domain NLP Pipeline
    analysis_data = analyze_comprehensive(
        resume_text=resume_text,
        target_job_role=job_role,
        job_description=job_description
    )
    
    # 2. Generate Explainable AI Prioritized Learning Roadmaps
    structured_recs = get_prioritized_recommendations(
        analysis_data["missing_skills"],
        analysis_data["missing_must_have"]
    )
    analysis_data["structured_recommendations"] = structured_recs
    analysis_data["recommendations"] = [
        f"[{r['priority']}] {r['skill']}: {r['topics']} | Project: {r['project_idea']}"
        for r in structured_recs
    ]
    
    # 3. Generate Strategic ATS Keyword & Section Advice
    strategic_advice = generate_strategic_advice(analysis_data)
    analysis_data["strategic_advice"] = strategic_advice

    # 4. Log Analysis in Database
    try:
        effective_role = analysis_data.get("job_role") or job_role or "Custom Job Description"
        log_analysis(
            current_user["id"],
            effective_role,
            analysis_data["composite_score"],
            analysis_data["matched_skills"],
            analysis_data["missing_skills"]
        )
    except Exception as db_err:
        print(f"Failed to log analysis to database: {db_err}")

    # Standardize match_score for backward compatibility
    analysis_data["match_score"] = analysis_data["composite_score"]

    return analysis_data

# DOWNLOAD SKILL GAP REPORT PDF ENDPOINT
class ReportDownloadPayload(BaseModel):
    analysis_data: dict

@app.post("/api/report/download")
async def api_download_report(
    payload: ReportDownloadPayload,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    try:
        temp_dir = tempfile.gettempdir()
        report_filename = os.path.join(temp_dir, f"Elevora_Report_{current_user['id']}_{os.getpid()}.pdf")
        generate_skill_gap_report_pdf(
            analysis_data=payload.analysis_data,
            user_name=current_user.get("username", "Candidate"),
            filename=report_filename
        )
        background_tasks.add_task(lambda p: os.remove(p) if os.path.exists(p) else None, report_filename)
        return FileResponse(
            report_filename,
            media_type="application/pdf",
            filename=f"Elevora_Skill_Gap_Report_{payload.analysis_data.get('job_role', 'Assessment').replace(' ', '_')}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report PDF: {str(e)}")

# ANALYSIS HISTORY ENDPOINT
@app.get("/api/history")
def api_history(current_user: dict = Depends(get_current_user)):
    try:
        history = load_analysis_history(current_user["id"])
        # Format dates nicely
        formatted_history = []
        for item in history:
            dt = item["analyzed_at"]
            dt_str = dt.strftime("%Y-%m-%d %H:%M") if hasattr(dt, "strftime") else str(dt)
            formatted_history.append({
                "job_role": item["job_role"],
                "match_score": round(item["match_score"], 1),
                "matched_skills": [s.strip() for s in item["matched_skills"].split(",") if s.strip()],
                "missing_skills": [s.strip() for s in item["missing_skills"].split(",") if s.strip()],
                "analyzed_at": dt_str
            })
        return formatted_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load history: {str(e)}")

# RESUME GENERATOR ENDPOINTS

@app.get("/api/resume/load")
def api_load_resume(current_user: dict = Depends(get_current_user)):
    try:
        resume = load_resume(current_user["id"])
        projects = load_projects(current_user["id"])
        
        # If no resume details exist, return empty template
        if not resume:
            return {
                "name": "", "phone": "", "email": "", "location": "", "linkedin": "",
                "objective": "", "education": "", "languages": "", "database": "",
                "tools": "", "concepts": "", "achievements": "", "activities": "",
                "extra_curricular": "", "projects": []
            }
            
        return {
            "name": resume.get("name") or "",
            "phone": resume.get("phone") or "",
            "email": resume.get("email") or "",
            "location": resume.get("location") or "",
            "linkedin": resume.get("linkedin") or "",
            "objective": resume.get("objective") or "",
            "education": resume.get("education") or "",
            "languages": resume.get("languages") or "",
            "database": resume.get("database") or "",
            "tools": resume.get("tools") or "",
            "concepts": resume.get("concepts") or "",
            "achievements": resume.get("achievements") or "",
            "activities": resume.get("activities") or "",
            "extra_curricular": resume.get("extra_curricular") or "",
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load resume profile: {str(e)}")

@app.post("/api/resume/save")
def api_save_resume(req: ResumeSaveRequest, current_user: dict = Depends(get_current_user)):
    try:
        proj_list = [{"title": p.title, "desc": p.desc} for p in req.projects]
        
        save_resume(
            current_user["id"], req.name, req.phone, req.email, req.location, req.linkedin,
            req.objective, req.education, req.languages, req.tools, req.concepts,
            req.achievements, req.activities, req.database, req.extra_curricular
        )
        save_projects(current_user["id"], proj_list)
        return {"success": True, "message": "Resume profile saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save resume profile: {str(e)}")

@app.post("/api/resume/generate")
def api_generate_resume(
    req: ResumeSaveRequest, 
    background_tasks: BackgroundTasks,
    template: str = Form("Classic ATS"), 
    current_user: dict = Depends(get_current_user)
):
    try:
        # 1. Save changes first
        proj_list = [{"title": p.title, "desc": p.desc} for p in req.projects]
        save_resume(
            current_user["id"], req.name, req.phone, req.email, req.location, req.linkedin,
            req.objective, req.education, req.languages, req.tools, req.concepts,
            req.achievements, req.activities, req.database, req.extra_curricular
        )
        save_projects(current_user["id"], proj_list)

        # 2. Generate PDF in OS temp directory
        temp_dir = tempfile.gettempdir()
        pdf_filename = f"Resume_User_{current_user['id']}_{os.getpid()}.pdf"
        pdf_path = os.path.join(temp_dir, pdf_filename)
        
        generate_pdf(
            name=req.name,
            phone=req.phone,
            email=req.email,
            location=req.location,
            linkedin=req.linkedin,
            objective=req.objective,
            education=req.education,
            languages=req.languages,
            database=req.database,
            tools=req.tools,
            concepts=req.concepts,
            projects=proj_list,
            achievements=req.achievements,
            activities=req.activities,
            extra_curricular=req.extra_curricular,
            template=template,
            filename=pdf_path
        )
        
        if os.path.exists(pdf_path):
            background_tasks.add_task(lambda p: os.remove(p) if os.path.exists(p) else None, pdf_path)
            return FileResponse(
                path=pdf_path,
                filename="Professional_ATS_Resume.pdf",
                media_type="application/pdf"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate PDF file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate resume: {str(e)}")

# Serve frontend landing page at root
@app.get("/")
def read_root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Welcome to Resume Skill Gap Analyzer. Static frontend not found."}

# Mount static files at /static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mount assets directory for templates image preview etc.
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
