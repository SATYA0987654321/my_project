import re
from typing import List, Dict, Any, Set

# Comprehensive built-in English stopwords list (zero external download dependencies)
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", 
    "but", "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", 
    "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", 
    "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", 
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", 
    "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", 
    "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", 
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", 
    "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", 
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", 
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", 
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", 
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", 
    "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", 
    "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", 
    "yours", "yourself", "yourselves"
}

# High-impact ATS action verbs for engineering, data science, and leadership
STRONG_ACTION_VERBS: Set[str] = {
    "architected", "accelerated", "analyzed", "automated", "built", "benchmarked", "collaborated",
    "created", "customized", "designed", "deployed", "developed", "directed", "engineered",
    "established", "evaluated", "executed", "expanded", "formulated", "generated", "implemented",
    "improved", "increased", "integrated", "launched", "lead", "led", "managed", "migrated",
    "modeled", "monitored", "optimized", "orchestrated", "overhauled", "pioneered", "programmed",
    "quantified", "reduced", "refactored", "resolved", "scaled", "spearheaded", "standardized",
    "streamlined", "structured", "trained", "transformed", "upgraded", "validated", "yielded"
}

def clean_text(text: str) -> str:
    """Standardizes whitespace, strips non-printable characters, and normalizes text."""
    if not text:
        return ""
    # Replace non-breaking spaces and linebreaks
    text = text.replace("\xa0", " ").replace("\r", "\n")
    # Normalize excessive whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def preprocess(text: str) -> List[str]:
    """Tokenizes text into clean lowercase words without stopwords."""
    cleaned = clean_text(text).lower()
    # Extract alphanumeric tokens, including special tech tokens like c++, c#, .net
    tokens = re.findall(r'\b[a-zA-Z0-9_\-\+\#\.]+\b', cleaned)
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]

def extract_ngrams(tokens: List[str], n: int = 2) -> List[str]:
    """Extracts contiguous n-grams from a list of tokens."""
    if len(tokens) < n:
        return []
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

def extract_all_ngrams(text: str, max_n: int = 3) -> Set[str]:
    """Extracts 1-grams, 2-grams, and 3-grams from raw text for multi-word skill matching."""
    cleaned = clean_text(text).lower()
    # Keep words with tech symbols like c++, c#, .net
    words = re.findall(r'[a-zA-Z0-9_\-\+\#\.]+', cleaned)
    
    ngrams: Set[str] = set()
    for w in words:
        if len(w) > 1:
            ngrams.add(w)
            
    for n in range(2, max_n + 1):
        for i in range(len(words) - n + 1):
            ngram = " ".join(words[i:i+n])
            ngrams.add(ngram)
            
    return ngrams

def segment_resume_sections(text: str) -> Dict[str, str]:
    """
    Segment resume into distinct semantic sections using heuristic boundary detection.
    Sections: contact, summary, skills, experience, education, projects, certifications.
    """
    cleaned = clean_text(text)
    lines = cleaned.split("\n")
    
    section_patterns = {
        "summary": r'^(summary|professional summary|objective|career objective|profile|about me)\b',
        "skills": r'^(skills|technical skills|skills & expertise|core competencies|technologies|tools)\b',
        "experience": r'^(experience|work experience|employment history|professional experience|internships|work history)\b',
        "education": r'^(education|academic background|qualifications|academic history)\b',
        "projects": r'^(projects|academic projects|personal projects|technical projects|key projects)\b',
        "certifications": r'^(certifications|licenses|certificates|achievements|awards|publications)\b'
    }
    
    current_section = "contact"
    sections: Dict[str, List[str]] = {
        "contact": [],
        "summary": [],
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": []
    }
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        matched_section = None
        for sec_name, pattern in section_patterns.items():
            if re.match(pattern, line_clean.lower()):
                matched_section = sec_name
                break
                
        if matched_section:
            current_section = matched_section
        else:
            sections[current_section].append(line_clean)
            
    return {k: "\n".join(v) for k, v in sections.items()}

def extract_quantifiable_metrics(text: str) -> Dict[str, Any]:
    """
    Identifies metrics and quantifiable impact indicators in resume text (numbers, %, $, x speedup, etc.).
    """
    cleaned = clean_text(text)
    
    # Patterns for quantifiable indicators
    patterns = [
        r'\b\d+(\.\d+)?\s*%',                                   # 35%, 99.9%
        r'\$\s*\d+([,\.]\d+)?\s*(k|m|b|million|billion|thousand)?', # $500k, $1.2M
        r'\b\d+\s*x\b',                                         # 5x, 10x
        r'\b\d+([,\.]\d+)?\s*(users|clients|customers|requests|queries|qps|rps|records|rows|gb|tb|pb)\b', # 100k users
        r'\breduced\s+by\s+\d+(\.\d+)?\s*%',                     # reduced by 25%
        r'\bincreased\s+by\s+\d+(\.\d+)?\s*%',                   # increased by 40%
        r'\b(top|first|1st|2nd|3rd)\s+(place|rank|percentile)\b' # 1st place, top 5%
    ]
    
    found_metrics = []
    for pattern in patterns:
        matches = re.finditer(pattern, cleaned, re.IGNORECASE)
        for m in matches:
            found_metrics.append(m.group(0).strip())
            
    # Count unique occurrences
    unique_metrics = list(set(found_metrics))
    score = min(100.0, len(unique_metrics) * 20.0) # 5 distinct metrics yield 100% impact score
    
    return {
        "metrics_found": unique_metrics,
        "count": len(unique_metrics),
        "impact_score": round(score, 1)
    }

def evaluate_action_verbs(text: str) -> Dict[str, Any]:
    """
    Detects strong action verbs in bullet points and evaluates recruiter action strength.
    """
    words = preprocess(text)
    detected_verbs = [w for w in words if w in STRONG_ACTION_VERBS]
    unique_verbs = list(set(detected_verbs))
    
    # Score calculation: 6+ distinct strong verbs yields 100%
    score = min(100.0, (len(unique_verbs) / 6.0) * 100.0)
    
    return {
        "action_verbs": unique_verbs,
        "count": len(unique_verbs),
        "action_score": round(score, 1)
    }

def evaluate_contact_info(text: str) -> Dict[str, Any]:
    """
    Validates presence of essential contact details (Email, Phone, LinkedIn, GitHub).
    """
    cleaned = clean_text(text)
    
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cleaned))
    has_phone = bool(re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', cleaned))
    has_linkedin = bool(re.search(r'linkedin\.com/in/[\w\-]+', cleaned, re.IGNORECASE))
    has_github = bool(re.search(r'github\.com/[\w\-]+', cleaned, re.IGNORECASE))
    
    items_present = sum([has_email, has_phone, has_linkedin, has_github])
    completeness_pct = (items_present / 4.0) * 100.0
    
    return {
        "has_email": has_email,
        "has_phone": has_phone,
        "has_linkedin": has_linkedin,
        "has_github": has_github,
        "completeness_pct": round(completeness_pct, 1)
    }