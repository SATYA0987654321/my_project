from typing import List, Dict, Any

# Structured Knowledge Base of Curated Learning Roadmaps and Projects
SKILL_ROADMAP_DATABASE: Dict[str, Dict[str, Any]] = {
    # Machine Learning & Deep Learning
    "Machine Learning": {
        "priority": "High",
        "category": "Machine Learning & Deep Learning",
        "topics": "Scikit-Learn, Feature Engineering, Supervised/Unsupervised Algorithms, Cross-Validation, Hyperparameter Tuning",
        "project": "End-to-End Customer Churn / Credit Risk Predictor with Streamlit/FastAPI UI and Model Explainability (SHAP).",
        "time": "3-4 Weeks",
        "ats_tip": "Include bullet point: 'Trained ensemble gradient-boosted models achieving 92% ROC-AUC on 100k customer records.'"
    },
    "Deep Learning": {
        "priority": "High",
        "category": "Machine Learning & Deep Learning",
        "topics": "PyTorch, Neural Network Architectures, Backpropagation, CNNs, Transfer Learning, GPU Training",
        "project": "Medical Image Classification or Defect Detection System with Transfer Learning (ResNet/EfficientNet).",
        "time": "4-5 Weeks",
        "ats_tip": "Detail dataset size and accuracy benchmarks in your project description."
    },
    "PyTorch": {
        "priority": "High",
        "category": "Machine Learning & Deep Learning",
        "topics": "Tensors, Autograd, Custom Datasets/Dataloaders, nn.Module, PyTorch Lightning",
        "project": "Custom Multi-Task Neural Network for Multimodal Sentiment Analysis.",
        "time": "3 Weeks",
        "ats_tip": "Highlight PyTorch deployment and custom loss functions implemented."
    },
    "TensorFlow": {
        "priority": "Medium",
        "category": "Machine Learning & Deep Learning",
        "topics": "tf.data, Keras Sequential & Functional APIs, SavedModel, TensorBoard",
        "project": "Time-Series Stock/Demand Forecasting Model with LSTM and Bidirectional GRUs.",
        "time": "3 Weeks",
        "ats_tip": "Mention model training optimizations and latency benchmarks."
    },
    "Scikit-Learn": {
        "priority": "High",
        "category": "Machine Learning & Deep Learning",
        "topics": "Pipeline API, ColumnTransformer, GridSearch/RandomSearch, Metrics (ROC-AUC, Precision-Recall)",
        "project": "Reproducible ML Pipeline with automated preprocessing and model evaluation.",
        "time": "2 Weeks",
        "ats_tip": "Emphasize modular pipelines and clean data transformations."
    },

    # NLP & GenAI
    "LLMs": {
        "priority": "High",
        "category": "NLP & GenAI",
        "topics": "Prompt Engineering, Few-Shot Prompting, Function Calling, Tokenization, Context Window Optimization",
        "project": "Enterprise Document Q&A Agent using GPT-4 / Llama-3 with Multi-Document Retrieval.",
        "time": "2-3 Weeks",
        "ats_tip": "Quantify latency reductions and hallucination mitigation techniques."
    },
    "Generative AI": {
        "priority": "High",
        "category": "NLP & GenAI",
        "topics": "Foundation Models, Diffusion Models, Autonomous Agents, Embeddings",
        "project": "AI-Powered Code Reviewer & Security Scanner Assistant using Agentic workflows.",
        "time": "3 Weeks",
        "ats_tip": "Highlight custom agent orchestration and tool usage."
    },
    "LangChain": {
        "priority": "High",
        "category": "NLP & GenAI",
        "topics": "Chains, PromptTemplates, OutputParsers, Memory, Tools & Agents",
        "project": "Autonomous Research Agent that crawls web sources and compiles structured executive briefs.",
        "time": "2 Weeks",
        "ats_tip": "Specify vector stores and LLM frameworks integrated."
    },
    "RAG": {
        "priority": "High",
        "category": "NLP & GenAI",
        "topics": "Chunking Strategies, Hybrid Search (Dense + Sparse), Re-ranking, Vector Similarity, Evaluation",
        "project": "Production-Grade Hybrid RAG System over complex Financial/Legal PDF filings.",
        "time": "2-3 Weeks",
        "ats_tip": "Highlight retrieval recall and context precision improvements."
    },
    "Vector Databases": {
        "priority": "High",
        "category": "NLP & GenAI",
        "topics": "ChromaDB, Pinecone, Qdrant, FAISS, Cosine & Dot-Product Indexing, Metadata Filtering",
        "project": "Scalable Semantic Search Engine over 500k technical articles with sub-50ms query response.",
        "time": "1-2 Weeks",
        "ats_tip": "Mention index scaling and queries-per-second (QPS) throughput."
    },
    "NLP": {
        "priority": "High",
        "category": "NLP & GenAI",
        "topics": "spaCy, Text Classification, Named Entity Recognition (NER), Sentiment Analysis, Transformers",
        "project": "Real-time Customer Support Ticket Categorization & Priority Routing Pipeline.",
        "time": "3 Weeks",
        "ats_tip": "Demonstrate business impact by mentioning automated ticket triage rates."
    },
    "Transformers": {
        "priority": "High",
        "category": "NLP & GenAI",
        "topics": "Self-Attention Mechanism, BERT, GPT, T5, Hugging Face Tokenizers & Pipeline API",
        "project": "Fine-Tuned BERT model for specialized Medical/Domain Named Entity Extraction.",
        "time": "3 Weeks",
        "ats_tip": "List F1-score improvements achieved over baseline models."
    },

    # Data Analysis & BI
    "SQL": {
        "priority": "High",
        "category": "Data Analysis & BI",
        "topics": "Window Functions (ROW_NUMBER, LEAD/LAG), CTEs, Indexing, Query Optimization, Subqueries",
        "project": "E-Commerce Revenue & Retention Cohort Analysis with advanced analytical SQL queries.",
        "time": "1-2 Weeks",
        "ats_tip": "Write: 'Engineered complex multi-table SQL queries processing 10M+ rows, reducing query execution time by 40%.'"
    },
    "Power BI": {
        "priority": "High",
        "category": "Data Analysis & BI",
        "topics": "DAX Formulas, Power Query ETL, Star-Schema Data Modeling, Interactive Drill-Down Reports",
        "project": "Executive Sales & Operational Dashboard with automated scheduled refresh and KPIs.",
        "time": "2 Weeks",
        "ats_tip": "Mention executive stakeholder adoption and time saved in manual reporting."
    },
    "Tableau": {
        "priority": "High",
        "category": "Data Analysis & BI",
        "topics": "LOD Expressions (Fixed, Include, Exclude), Calculated Fields, Dashboard Actions, Storyboards",
        "project": "Global Supply Chain Logistics & Carbon Footprint Interactive Tableau Dashboard.",
        "time": "2 Weeks",
        "ats_tip": "Showcase portfolio links to Tableau Public on your resume."
    },
    "Excel": {
        "priority": "Medium",
        "category": "Data Analysis & BI",
        "topics": "XLOOKUP, Pivot Tables, Power Pivot, Data Validation, What-If Analysis, VBA/Macros",
        "project": "Automated Financial Forecasting & Budget Tracking Model with Dynamic Scenario Analysis.",
        "time": "1 Week",
        "ats_tip": "Highlight financial or operational modeling capabilities."
    },
    "Data Analysis": {
        "priority": "High",
        "category": "Data Analysis & BI",
        "topics": "Exploratory Data Analysis (EDA), Hypothesis Testing, Missing Data Imputation, Correlation Analysis",
        "project": "Comprehensive Market Basket & Consumer Behavior Analysis on Public Datasets.",
        "time": "2 Weeks",
        "ats_tip": "Highlight actionable findings derived that improved business KPIs."
    },
    "Statistics": {
        "priority": "High",
        "category": "Data Analysis & BI",
        "topics": "Probability Distributions, Central Limit Theorem, Hypothesis Testing (p-values, z-test, t-test), ANOVA",
        "project": "Statistical Analysis of A/B Experiment Results with statistical power and sample sizing.",
        "time": "2 Weeks",
        "ats_tip": "Emphasize confidence intervals and statistical significance testing."
    },

    # Big Data & Cloud
    "Apache Spark": {
        "priority": "High",
        "category": "Big Data & Cloud",
        "topics": "PySpark DataFrames, Spark SQL, RDD Operations, Partitioning, Broadcast Joins, Spark Streaming",
        "project": "Distributed Log Analytics & Fraud Detection Pipeline processing 50GB streaming data.",
        "time": "3-4 Weeks",
        "ats_tip": "Mention cluster configurations, partition tuning, and processing throughput."
    },
    "Airflow": {
        "priority": "High",
        "category": "Big Data & Cloud",
        "topics": "DAG Architecture, PythonOperator, BashOperator, Task Dependencies, Sensors, Backfilling",
        "project": "Production Automated Daily ETL Pipeline with Slack alerts and failure retry policies.",
        "time": "2 Weeks",
        "ats_tip": "Write: 'Orchestrated automated data pipelines via Apache Airflow, processing daily ETL workflows.'"
    },
    "AWS": {
        "priority": "High",
        "category": "Big Data & Cloud",
        "topics": "S3, EC2, RDS, Lambda (Serverless), SageMaker (ML), CloudWatch, IAM Roles",
        "project": "Serverless Data Ingestion & ML Inference Pipeline deployed on AWS Lambda & S3.",
        "time": "3 Weeks",
        "ats_tip": "List specific AWS services used and cost-reduction achievements."
    },
    "Docker": {
        "priority": "High",
        "category": "DevOps & MLOps",
        "topics": "Dockerfile Optimization, Multi-Stage Builds, Docker Compose, Port Forwarding, Volume Mounts",
        "project": "Containerized Microservices Application combining FastAPI backend, Redis cache, and Postgres.",
        "time": "1-2 Weeks",
        "ats_tip": "Highlight containerization of models for reproducible cross-environment deployments."
    },
    "Kubernetes": {
        "priority": "High",
        "category": "DevOps & MLOps",
        "topics": "Pods, Deployments, Services, Ingress, Horizontal Pod Autoscaling (HPA), ConfigMaps",
        "project": "Auto-scaling ML Model Serving Cluster on Minikube / EKS with Ingress routing.",
        "time": "3-4 Weeks",
        "ats_tip": "Mention zero-downtime rolling deployments and cluster scaling."
    },
    "MLOps": {
        "priority": "High",
        "category": "DevOps & MLOps",
        "topics": "MLflow, DVC, Model Registry, Automated Retraining, Data Drift Monitoring (Evidently AI)",
        "project": "Automated End-to-End MLOps Pipeline with Continuous Training and Model Monitoring.",
        "time": "3-4 Weeks",
        "ats_tip": "Highlight drift detection and automated model rollback strategies."
    },
    "FastAPI": {
        "priority": "High",
        "category": "Web & API",
        "topics": "Pydantic Models, Async Handlers, Dependency Injection, JWT Authentication, OpenAPI Documentation",
        "project": "High-Throughput Asynchronous REST API serving ML predictions with sub-20ms latency.",
        "time": "1-2 Weeks",
        "ats_tip": "Include benchmark requests-per-second (RPS) metrics in resume."
    },
    "Git": {
        "priority": "High",
        "category": "DevOps & MLOps",
        "topics": "Branching Strategies (GitFlow), Rebase, Merge Conflicts, Pull Requests, GitHub Actions CI/CD",
        "project": "Automated CI/CD GitHub Action that runs unit tests, lints code, and deploys on merge.",
        "time": "1 Week",
        "ats_tip": "Emphasize collaboration in Agile teams and continuous integration practices."
    }
}


def get_prioritized_recommendations(
    missing_skills: List[str],
    missing_must_have: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Generates structured, explainable AI learning roadmaps for missing skills.
    Categorizes urgency (High / Medium / Low) and provides concrete projects and ATS keyword advice.
    """
    missing_must_have_set = set(missing_must_have or [])
    recommendations = []
    
    for skill in missing_skills:
        skill_clean = skill.strip()
        data = SKILL_ROADMAP_DATABASE.get(skill_clean)
        
        # Determine priority based on must-have status or database default
        if skill_clean in missing_must_have_set:
            priority = "High (Critical)"
            badge_class = "badge-high"
        elif data and data.get("priority") == "High":
            priority = "High"
            badge_class = "badge-high"
        elif data and data.get("priority") == "Medium":
            priority = "Medium"
            badge_class = "badge-medium"
        else:
            priority = "Low (Supplementary)"
            badge_class = "badge-low"
            
        if data:
            recommendations.append({
                "skill": skill_clean,
                "category": data["category"],
                "priority": priority,
                "badge_class": badge_class,
                "topics": data["topics"],
                "project_idea": data["project"],
                "estimated_time": data["time"],
                "ats_tip": data["ats_tip"]
            })
        else:
            recommendations.append({
                "skill": skill_clean,
                "category": "Technical Skill",
                "priority": priority,
                "badge_class": badge_class,
                "topics": f"Core concepts, syntax, and best practices for {skill_clean}",
                "project_idea": f"Build a practical hands-on portfolio application implementing {skill_clean}.",
                "estimated_time": "1-2 Weeks",
                "ats_tip": f"Add a concise bullet point in your Experience or Projects section demonstrating {skill_clean} usage."
            })
            
    # Sort: High priority first, then Medium, then Low
    priority_order = {"High (Critical)": 0, "High": 1, "Medium": 2, "Low (Supplementary)": 3, "Low": 4}
    return sorted(recommendations, key=lambda x: priority_order.get(x["priority"], 5))


def get_recommendations(missing: List[str]) -> List[str]:
    """Backward-compatible simple string list helper."""
    structured = get_prioritized_recommendations(missing)
    return [
        f"[{r['priority']}] {r['skill']}: {r['topics']} | Project: {r['project_idea']}"
        for r in structured
    ]


def generate_strategic_advice(
    analysis_result: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Generates tailored strategic tips based on candidate scores (ATS Format, Impact, Skills).
    """
    advice = []
    sub_scores = analysis_result.get("sub_scores", {})
    sec_analysis = analysis_result.get("section_analysis", {})
    metrics = analysis_result.get("quantifiable_metrics", {})
    verbs = analysis_result.get("action_verbs", {})
    
    # 1. Section Gaps Advice
    missing_secs = sec_analysis.get("missing_sections", [])
    if missing_secs:
        advice.append({
            "type": "format",
            "title": f"Missing Core Sections: {', '.join(missing_secs)}",
            "text": f"Recruiter ATS scanners look for standard section headers. Consider explicitly adding a '{missing_secs[0]}' section to improve structural parsing."
        })
        
    # 2. Quantifiable Impact Advice
    if metrics.get("count", 0) < 3:
        advice.append({
            "type": "impact",
            "title": "Quantify Your Achievements with Metrics",
            "text": "Your resume currently contains few measurable metrics. Add quantifiable results like percentage increases (e.g. 'boosted accuracy by 18%'), latency drops, or user counts to stand out."
        })
        
    # 3. Action Verb Advice
    if verbs.get("count", 0) < 4:
        advice.append({
            "type": "verbs",
            "title": "Strengthen Action Verbs in Bullet Points",
            "text": "Start your experience bullet points with strong action verbs (e.g. 'Architected', 'Spearheaded', 'Optimized', 'Engineered') instead of passive phrases like 'Worked on' or 'Responsible for'."
        })
        
    # 4. Critical Skills Advice
    missing_must = analysis_result.get("missing_must_have", [])
    if missing_must:
        advice.append({
            "type": "skills",
            "title": f"Must-Have Skills Gap ({len(missing_must)} Critical)",
            "text": f"Prioritize learning {', '.join(missing_must[:3])} to immediately boost your candidate match score for {analysis_result.get('job_role')}."
        })
        
    return advice