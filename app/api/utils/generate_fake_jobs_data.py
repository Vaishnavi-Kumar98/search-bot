import random
import json
from faker import Faker

fake = Faker()

# Use the same role_groups you defined earlier
role_groups = {
    "Data Scientist": {
        "titles": [
            "Data Scientist", "Machine Learning Engineer", "AI Specialist",
            "Data Analyst (ML)", "Research Scientist (AI)"
        ],
        "skills": [
            ["Python", "Machine Learning", "Data Analysis", "TensorFlow", "Statistics"],
            ["Python", "ML", "Deep Learning", "Pandas", "Numpy"],
            ["AI", "Neural Networks", "Data Mining", "PyTorch", "Mathematics"],
            ["Data Modelling", "Predictive Analytics", "SciKit-Learn", "ML Pipelines", "EDA"],
            ["Natural Language Processing", "Computer Vision", "Model Deployment", "Feature Engineering", "ML Ops"]
        ],
        "exp_range": (24, 96),   # in months
        "salary_range": (8.0, 35.0)
    },
    "Backend Developer": {
        "titles": [
            "Backend Developer", "Backend Engineer", "API Developer",
            "Server-Side Developer", "Software Engineer (Backend)"
        ],
        "skills": [
            ["Python", "FastAPI", "PostgreSQL", "REST APIs", "Django"],
            ["Java", "Spring Boot", "MySQL", "REST APIs", "Hibernate"],
            ["Node.js", "Express", "MongoDB", "GraphQL", "API Security"],
            ["Go", "gRPC", "PostgreSQL", "Caching", "Load Balancing"],
            ["Ruby", "Rails", "PostgreSQL", "API Testing", "Docker"]
        ],
        "exp_range": (18, 84),
        "salary_range": (6.0, 30.0)
    },
    "Frontend Developer": {
        "titles": [
            "Frontend Developer", "UI Engineer", "React Developer",
            "Web Developer (Frontend)", "JavaScript Engineer"
        ],
        "skills": [
            ["JavaScript", "React", "CSS", "HTML", "TypeScript"],
            ["Vue.js", "JavaScript", "SCSS", "Bootstrap", "HTML5"],
            ["Angular", "TypeScript", "CSS3", "Responsive Design", "RxJS"],
            ["React", "TailwindCSS", "Next.js", "JavaScript", "Styled Components"],
            ["Svelte", "JavaScript", "CSS Grid", "Flexbox", "HTML5"]
        ],
        "exp_range": (12, 72),
        "salary_range": (5.0, 25.0)
    },
    "DevOps Engineer": {
        "titles": [
            "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
            "Infrastructure Engineer", "Platform Engineer"
        ],
        "skills": [
            ["AWS", "Docker", "Kubernetes", "CI/CD", "Terraform"],
            ["Azure", "Kubernetes", "Helm", "GitLab CI", "Infrastructure as Code"],
            ["GCP", "Docker Swarm", "Ansible", "Jenkins", "Monitoring"],
            ["AWS", "CloudFormation", "Bash", "Prometheus", "Grafana"],
            ["Kubernetes", "Terraform", "AWS Lambda", "ECS", "Security"]
        ],
        "exp_range": (24, 108),
        "salary_range": (8.0, 40.0)
    },
    "Data Engineer": {
        "titles": [
            "Data Engineer", "ETL Developer", "Big Data Engineer",
            "Pipeline Engineer", "Data Infrastructure Engineer"
        ],
        "skills": [
            ["SQL", "ETL", "Apache Spark", "Data Warehousing", "Airflow"],
            ["Hadoop", "Hive", "ETL", "Spark Streaming", "Data Pipelines"],
            ["Snowflake", "dbt", "Airflow", "Data Modeling", "Cloud Dataflow"],
            ["AWS Glue", "Athena", "Redshift", "ETL", "S3"],
            ["Kafka", "Spark", "Data Lakes", "Delta Lake", "ETL"]
        ],
        "exp_range": (24, 96),
        "salary_range": (8.0, 38.0)
    }
}

cities = ["Bangalore", "Mumbai", "Delhi", "Pune", "Hyderabad"]

jobs = []
job_counter = 1

for _ in range(50):
    role_key = random.choice(list(role_groups.keys()))
    details = role_groups[role_key]

    job_title = random.choice(details["titles"])
    job_skills = random.choice(details["skills"])
    exp_required = random.randint(*details["exp_range"])
    annual_ctc = round(random.uniform(*details["salary_range"]), 2)

    job = {
        "job_id": f"job-{job_counter}",
        "job_summary": fake.paragraph(nb_sentences=3),
        "skills": job_skills,
        "job_title": job_title,
        "job_role": role_key,
        "total_months_of_experience": exp_required,
        "location": random.sample(cities, 2),
        "annual_ctc": annual_ctc,
        "created_by": "admin",
        "updated_by": "admin",
        "created_at": int(fake.date_time_this_year().timestamp()),
    }

    jobs.append(job)
    job_counter += 1

with open("jobs.json", "w") as f:
    json.dump(jobs, f, indent=2)

print(f"Generated {len(jobs)} jobs in jobs.json")
