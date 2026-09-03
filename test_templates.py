from utils.generator import generate_pdf

def test_generation():
    name = "Lokesh Kumar"
    phone = "+91 98765 43210"
    email = "kr.lokeshbxr10@gmail.com"
    location = "Indore, India"
    linkedin = "linkedin.com/in/lokeshkumar"
    objective = "Highly skilled software engineer with 5+ years of experience building scalable web applications. Passionate about AI integration, clean architecture, and performance optimization."
    education = "University of California, Berkeley | B.S. in Computer Science | 2018 - 2022"
    languages = "Python, Java, JavaScript, C++, SQL"
    database = "PostgreSQL, MySQL, Redis, MongoDB"
    tools = "Streamlit, ReportLab, Docker, Git, AWS"
    concepts = "Data Structures, Algorithms, REST APIs, System Design, CI/CD"
    
    projects = [
        {
            "title": "AI Resume Gap Analyzer",
            "desc": "Tech: Python, Streamlit, NLP, MySQL\n- Built an AI-driven tool to parse resumes and detect skills gaps against job listings.\n- Integrated semantic NLP analysis to calculate keyword alignment match score.\n- Used ReportLab to dynamically generate high-quality ATS-friendly PDF profiles."
        },
        {
            "title": "Distributed Task Queue",
            "desc": "Tech: Go, Redis, Docker, gRPC\n- Developed a light-weight distributed task executor matching Celery API capabilities.\n- Reduced message transit latency by 35% using binary serialization protocols.\n- Implemented custom retry policies with exponential backoff algorithm."
        }
    ]
    
    achievements = "- Winner of SF Hackathon 2023 out of 150+ competing teams.\n- Published research paper on NLP keyword extraction in local IEEE symposium."
    activities = "- Active open source contributor to Python NLP and web parsing libraries.\n- Mentor at code camp teaching basic algorithm design to high schoolers."
    extra_curricular = "- Captain of the university chess team.\n- Finished full marathon (26.2 miles) in under 4 hours."

    print("Generating Classic ATS template...")
    generate_pdf(
        name, phone, email, location, linkedin,
        objective, education, languages, database, tools, concepts,
        projects, achievements, activities, extra_curricular,
        template="Classic ATS", filename="test_output_classic_ats.pdf"
    )

    print("Generating Modern Minimalist template...")
    generate_pdf(
        name, phone, email, location, linkedin,
        objective, education, languages, database, tools, concepts,
        projects, achievements, activities, extra_curricular,
        template="Modern Minimalist", filename="test_output_modern_minimalist.pdf"
    )

    print("Generating Elegant Executive template...")
    generate_pdf(
        name, phone, email, location, linkedin,
        objective, education, languages, database, tools, concepts,
        projects, achievements, activities, extra_curricular,
        template="Elegant Executive", filename="test_output_elegant_executive.pdf"
    )
    print("All templates generated successfully!")

if __name__ == "__main__":
    test_generation()
