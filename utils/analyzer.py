import os
import re
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Set, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.nlp import (
    clean_text,
    preprocess,
    extract_all_ngrams,
    segment_resume_sections,
    extract_quantifiable_metrics,
    evaluate_action_verbs,
    evaluate_contact_info
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SKILLS_PATH = os.path.join(BASE_DIR, "data", "skills.csv")
JOBS_PATH = os.path.join(BASE_DIR, "data", "jobs.csv")

# Structure: { normalized_alias_or_name: (canonical_name, category) }
SKILL_TAXONOMY: Dict[str, Tuple[str, str]] = {}
ALL_CANONICAL_SKILLS: Dict[str, str] = {} # canonical_name -> category
skills_df = pd.DataFrame()
jobs_df = pd.DataFrame()

def load_taxonomies():
    global skills_df, jobs_df, SKILL_TAXONOMY, ALL_CANONICAL_SKILLS
    skills_df = pd.read_csv(SKILLS_PATH).fillna("")
    jobs_df = pd.read_csv(JOBS_PATH).fillna("")
    
    SKILL_TAXONOMY.clear()
    ALL_CANONICAL_SKILLS.clear()
    
    for _, row in skills_df.iterrows():
        canonical = str(row["Skill"]).strip()
        category = str(row.get("Category", "")).strip() or "General Tech"
        ALL_CANONICAL_SKILLS[canonical] = category
        SKILL_TAXONOMY[canonical.lower()] = (canonical, category)
        
        aliases = str(row.get("Aliases", ""))
        if aliases:
            for alias in aliases.split(","):
                alias_clean = alias.strip().lower()
                if alias_clean:
                    SKILL_TAXONOMY[alias_clean] = (canonical, category)

# Initial load
load_taxonomies()


def get_job_roles() -> List[Dict[str, Any]]:
    """Returns all available job roles with their metadata."""
    if jobs_df.empty:
        load_taxonomies()
        
    roles = []
    for _, row in jobs_df.iterrows():
        must_have = [s.strip() for s in str(row["Must_Have_Skills"]).split(",") if s.strip()]
        good_to_have = [s.strip() for s in str(row.get("Good_To_Have_Skills", "")).split(",") if s.strip()]
        roles.append({
            "role": str(row["Job Role"]),
            "category": str(row.get("Category", "Technology")),
            "must_have_skills": must_have,
            "good_to_have_skills": good_to_have,
            "all_skills": must_have + good_to_have,
            "description": str(row.get("Benchmark_Description", "")),
            "experience_level": str(row.get("Experience_Level", "All Levels"))
        })
    return roles


def extract_skills_with_metadata(text: str) -> Dict[str, Any]:
    """
    Extracts skills using N-gram extraction and alias matching against the 250+ skills taxonomy.
    Returns detected canonical skills, their categories, and category counts.
    """
    if not text:
        return {"skills": [], "by_category": {}, "categories_present": []}
        
    ngrams = extract_all_ngrams(text, max_n=3)
    cleaned_lower = clean_text(text).lower()
    
    detected_canonical: Set[str] = set()
    category_map: Dict[str, List[str]] = {}
    
    # Check both ngrams and exact boundary matches
    for term, (canonical, category) in SKILL_TAXONOMY.items():
        if term in ngrams:
            detected_canonical.add(canonical)
        elif len(term) > 3 and re.search(r'\b' + re.escape(term) + r'\b', cleaned_lower):
            detected_canonical.add(canonical)
            
    detected_list = sorted(list(detected_canonical))
    
    for skill in detected_list:
        cat = ALL_CANONICAL_SKILLS.get(skill, "General Tech")
        category_map.setdefault(cat, []).append(skill)
        
    return {
        "skills": detected_list,
        "by_category": category_map,
        "categories_present": list(category_map.keys())
    }


def extract_skills(text: str) -> List[str]:
    """Backward-compatible helper returning a list of extracted skill names."""
    return extract_skills_with_metadata(text)["skills"]


def calculate_tfidf_similarity(resume_text: str, benchmark_description: str) -> float:
    """
    Computes TF-IDF Cosine Similarity between resume text and benchmark role description.
    Uses 1-gram and 2-gram TF-IDF vectorization with sublinear term frequency scaling
    and information retrieval relevance normalization.
    """
    if not resume_text or not benchmark_description:
        return 0.0
        
    try:
        corpus = [clean_text(resume_text), clean_text(benchmark_description)]
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words='english',
            sublinear_tf=True,
            max_features=5000
        )
        tfidf_matrix = vectorizer.fit_transform(corpus)
        sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        raw_sim = float(sim_matrix[0][0])
        
        # Information Retrieval normalization for variable-length document vs query matching
        if raw_sim <= 0.001:
            return 0.0
        normalized_score = min(100.0, max(0.0, (raw_sim ** 0.5) * 100.0))
        return round(normalized_score, 1)
    except Exception as e:
        print(f"TF-IDF calculation fallback: {e}")
        return 50.0


def calculate_category_breakdown(
    detected_skills: List[str],
    job_skills: List[str]
) -> List[Dict[str, Any]]:
    """
    Calculates percentage match for each distinct technical category relevant to the job.
    """
    category_totals: Dict[str, List[str]] = {}
    
    # Determine all categories involved in the job
    for skill in job_skills:
        cat = ALL_CANONICAL_SKILLS.get(skill, "Core Skills")
        category_totals.setdefault(cat, []).append(skill)
        
    breakdown = []
    for cat, req_skills in category_totals.items():
        matched_in_cat = [s for s in req_skills if s in detected_skills]
        pct = (len(matched_in_cat) / len(req_skills) * 100.0) if req_skills else 0.0
        breakdown.append({
            "category": cat,
            "required_count": len(req_skills),
            "matched_count": len(matched_in_cat),
            "score": round(pct, 1),
            "matched_skills": matched_in_cat,
            "missing_skills": [s for s in req_skills if s not in detected_skills]
        })
        
    return sorted(breakdown, key=lambda x: x["score"], reverse=True)


def evaluate_section_completeness(sections: Dict[str, str]) -> Dict[str, Any]:
    """Evaluates presence and quality of standard resume sections."""
    core_sections = ["summary", "skills", "experience", "education", "projects"]
    detected = []
    missing = []
    
    for sec in core_sections:
        content = sections.get(sec, "").strip()
        if content and len(content) > 20:
            detected.append(sec.capitalize())
        else:
            missing.append(sec.capitalize())
            
    score = (len(detected) / len(core_sections)) * 100.0
    return {
        "detected_sections": detected,
        "missing_sections": missing,
        "completeness_score": round(score, 1)
    }


GENERIC_EXCLUSIONS = {
    "data analysis", "cloud computing", "algorithms", "supervised learning",
    "unsupervised learning", "reinforcement learning", "general tech", "oop",
    "big data & cloud", "mobile & cross-platform", "web & api", "research",
    "database design", "hardware protocols", "network protocols", "microcontrollers",
    "user stories", "user research", "usability testing", "wireframing", "prototyping",
    "communication", "problem solving", "team collaboration", "technical documentation"
}


def analyze_comprehensive(
    resume_text: str,
    target_job_role: Optional[str] = None,
    job_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main Multi-Domain NLP & Data Science analysis engine.
    Focuses strictly on the main required concrete technical skills.
    """
    must_have = []
    good_to_have = []
    role_category = "Technology"
    exp_level = "All Levels"
    
    jd_clean = (job_description or "").strip()
    
    # 1. If user provided a custom Job Description (JD)
    if jd_clean:
        # Check for explicit Must-Have and Desired sections in the JD
        must_have_match = re.search(r'(?:must[- ]have(?: skills)?|key requirements|core skills|mandatory skills?):\s*([^\n]+)', jd_clean, re.IGNORECASE)
        good_have_match = re.search(r'(?:desired|good[- ]to[- ]have|secondary(?: tools)?|nice[- ]to[- ]have|preferred skills?):\s*([^\n]+)', jd_clean, re.IGNORECASE)
        
        extracted_must = []
        extracted_good = []
        
        if must_have_match:
            must_text = must_have_match.group(1)
            extracted_must = [s for s in extract_skills_with_metadata(must_text)["skills"] if s.lower() not in GENERIC_EXCLUSIONS]
            
        if good_have_match:
            good_text = good_have_match.group(1)
            extracted_good = [s for s in extract_skills_with_metadata(good_text)["skills"] if s.lower() not in GENERIC_EXCLUSIONS]
            
        # Extract all skills present across full JD
        raw_jd_skills = extract_skills_with_metadata(jd_clean)["skills"]
        filtered_all_jd_skills = [s for s in raw_jd_skills if s.lower() not in GENERIC_EXCLUSIONS]
        
        # Determine Target Job Role Name
        if target_job_role and target_job_role.strip():
            final_role_name = target_job_role.strip()
        else:
            first_line = jd_clean.split("\n")[0].strip()
            if len(first_line) <= 60 and len(first_line) > 3 and not first_line.lower().startswith("we are") and not first_line.lower().startswith("position") and not first_line.lower().startswith("key"):
                final_role_name = first_line.replace("#", "").strip()
            else:
                final_role_name = "Target Job Description"
                for _, r in jobs_df.iterrows():
                    if r["Job Role"].lower() in jd_clean.lower()[:300]:
                        final_role_name = r["Job Role"]
                        break
        
        role_row = jobs_df[jobs_df["Job Role"].str.lower() == final_role_name.lower()]
        if not role_row.empty:
            r = role_row.iloc[0]
            role_category = str(r.get("Category", "Technology"))
            exp_level = str(r.get("Experience_Level", "Mid Level"))
        
        if extracted_must or extracted_good:
            must_have = extracted_must
            good_to_have = extracted_good
            # Any remaining skills detected in full JD text go to good_to_have
            for s in filtered_all_jd_skills:
                if s not in must_have and s not in good_to_have:
                    good_to_have.append(s)
        else:
            # Free-form JD text
            if filtered_all_jd_skills:
                cutoff = max(1, int(len(filtered_all_jd_skills) * 0.65))
                must_have = filtered_all_jd_skills[:cutoff]
                good_to_have = filtered_all_jd_skills[cutoff:]
            else:
                must_have = ["Python", "SQL", "Git"]
                good_to_have = ["Docker", "Linux"]
            
        benchmark_desc = jd_clean
        benchmark_corpus = f"{final_role_name}. {jd_clean}"
        
    else:
        # Predefined role from streamlined taxonomy
        final_role_name = target_job_role or "Data Science"
        role_row = jobs_df[jobs_df["Job Role"].str.lower() == final_role_name.lower()]
        if role_row.empty:
            must_have = ["Python", "SQL", "Machine Learning", "Statistics"]
            good_to_have = ["Scikit-Learn", "PyTorch"]
            benchmark_desc = final_role_name
            role_category = "Data Science & AI"
            exp_level = "All Levels"
        else:
            r = role_row.iloc[0]
            must_have = [s.strip() for s in r["Must_Have_Skills"].split(",") if s.strip() and s.strip().lower() not in GENERIC_EXCLUSIONS]
            good_to_have = [s.strip() for s in str(r.get("Good_To_Have_Skills", "")).split(",") if s.strip() and s.strip().lower() not in GENERIC_EXCLUSIONS]
            benchmark_desc = str(r.get("Benchmark_Description", ""))
            role_category = str(r.get("Category", "Technology"))
            exp_level = str(r.get("Experience_Level", "Mid Level"))
            
        benchmark_corpus = f"{final_role_name}. Core Skills: {', '.join(must_have)}. Desired: {', '.join(good_to_have)}. {benchmark_desc}"
        
    all_job_skills = list(dict.fromkeys(must_have + good_to_have))
    
    # 2. Extract Candidate Skills & Taxonomy
    extraction_res = extract_skills_with_metadata(resume_text)
    detected_skills = extraction_res["skills"]
    
    # 3. Partition Matched & Missing Skills
    matched_must_have = [s for s in must_have if s in detected_skills]
    missing_must_have = [s for s in must_have if s not in detected_skills]
    
    matched_good_to_have = [s for s in good_to_have if s in detected_skills]
    missing_good_to_have = [s for s in good_to_have if s not in detected_skills]
    
    all_matched = [s for s in all_job_skills if s in detected_skills]
    all_missing = [s for s in all_job_skills if s not in detected_skills]
    extra_skills = [s for s in detected_skills if s not in all_job_skills]
    
    # 4. Multi-Dimensional Scoring
    must_have_pct = (len(matched_must_have) / len(must_have) * 100.0) if must_have else 100.0
    good_to_have_pct = (len(matched_good_to_have) / len(good_to_have) * 100.0) if good_to_have else 100.0
    skill_coverage_score = (must_have_pct * 0.70) + (good_to_have_pct * 0.30)
    
    # TF-IDF Cosine Similarity directly against the JD text
    semantic_similarity = calculate_tfidf_similarity(resume_text, benchmark_corpus)
    
    # NLP Section & Impact Evaluation
    sections = segment_resume_sections(resume_text)
    sec_eval = evaluate_section_completeness(sections)
    contact_eval = evaluate_contact_info(resume_text)
    metric_eval = extract_quantifiable_metrics(resume_text)
    action_eval = evaluate_action_verbs(resume_text)
    
    # ATS Format Health Score (50% section completeness + 50% contact info)
    ats_format_score = round((sec_eval["completeness_score"] * 0.6) + (contact_eval["completeness_pct"] * 0.4), 1)
    
    # Quantifiable Impact & Action Verb Score
    impact_score = round((metric_eval["impact_score"] * 0.5) + (action_eval["action_score"] * 0.5), 1)
    
    # Composite Final Readiness Score (Strictly gated at 0% when 0 skills match)
    if len(all_matched) == 0:
        composite_score = 0.0
        semantic_similarity = 0.0
        match_tier = "No Match (0% Skill Alignment)"
        tier_color = "danger"
    else:
        composite_score = (
            (must_have_pct * 0.40) +
            (good_to_have_pct * 0.15) +
            (semantic_similarity * 0.25) +
            (ats_format_score * 0.10) +
            (impact_score * 0.10)
        )
        composite_score = min(100.0, max(0.0, round(composite_score, 1)))
        
        # Performance Tier Rating
        if composite_score >= 80.0:
            match_tier = "High Match (ATS Ready)"
            tier_color = "success"
        elif composite_score >= 50.0:
            match_tier = "Moderate Match (Targeted Gaps)"
            tier_color = "warning"
        else:
            match_tier = "Low Match (Action Required)"
            tier_color = "danger"
            
    # Category Breakdown
    category_breakdown = calculate_category_breakdown(detected_skills, all_job_skills)
        
    return {
        "job_role": final_role_name,
        "job_description": benchmark_desc,
        "job_category": role_category,
        "experience_level": exp_level,
        "composite_score": composite_score,
        "match_tier": match_tier,
        "tier_color": tier_color,
        "sub_scores": {
            "skill_coverage": round(skill_coverage_score, 1),
            "must_have_score": round(must_have_pct, 1),
            "good_to_have_score": round(good_to_have_pct, 1),
            "semantic_similarity": semantic_similarity,
            "ats_format_score": ats_format_score,
            "impact_score": impact_score
        },
        "matched_skills": all_matched,
        "matched_must_have": matched_must_have,
        "matched_good_to_have": matched_good_to_have,
        "missing_skills": all_missing,
        "missing_must_have": missing_must_have,
        "missing_good_to_have": missing_good_to_have,
        "extra_skills": extra_skills,
        "category_breakdown": category_breakdown,
        "section_analysis": sec_eval,
        "contact_info": contact_eval,
        "quantifiable_metrics": metric_eval,
        "action_verbs": action_eval
    }


def analyze(resume_skills: List[str], job_skills: List[str]) -> Tuple[List[str], List[str]]:
    """Backward-compatible simple set analysis."""
    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))
    return matched, missing


def match_score(matched: List[str], job_skills: List[str]) -> float:
    """Backward-compatible simple ratio score."""
    if not job_skills:
        return 0.0
    return (len(matched) / len(job_skills)) * 100.0