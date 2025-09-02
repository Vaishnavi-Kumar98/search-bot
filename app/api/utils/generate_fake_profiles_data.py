import random
import json
from faker import Faker
from datetime import datetime

fake = Faker()


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

profiles = []
id_counter = 1

for role_key, details in role_groups.items():
    for _ in range(20):
        first_name = fake.first_name()
        last_name = fake.last_name()

        # Random job title and skills from the group
        job_title = random.choice(details["titles"])
        skills = random.choice(details["skills"])

        # Random experience & salary in the role's range
        total_exp_months = random.randint(*details["exp_range"])
        current_ctc = round(random.uniform(*details["salary_range"]), 2)
        expected_ctc = round(current_ctc * random.uniform(1.05, 1.3), 2)

        # Employment history
        employment_history = [
            {
                "organisation_name": fake.company(),
                "job_title": job_title,
                "role": role_key,  # canonical role for grouping
                "industry": random.choice(["IT", "Software", "Analytics", "Cloud Services"]),
                "employment_type": random.choice(["Full-time", "Contract"]),
                "is_current_job": 1
            }
        ]

        # Education details
        highest_year = random.randint(2015, 2023)
        education_details = [
            {
                "education_level": random.choice(["Bachelor's Degree", "Master's Degree"]),
                "course_name": random.choice([
                    "Computer Science", "Information Technology", "Data Science", "Software Engineering"
                ]),
                "specialization": random.choice([
                    "AI", "Cloud Computing", "Machine Learning", "Big Data", "Web Development"
                ]),
                "year_of_completion": highest_year,
                "course_type": random.choice(["Full-time", "Part-time"]),
                "is_highest_qualification": 1
            }
        ]

        profile = {
            "id": f"cand-{id_counter}",
            "first_name": first_name,
            "last_name": last_name,
            "primary_mobile_number": fake.msisdn(),
            "primary_email": fake.email(),
            "current_city": random.choice(cities),
            "preferred_cities": random.sample(cities, 2),
            "total_months_of_experience": total_exp_months,
            "skills": skills,
            "employment_history": employment_history,
            "education_details": education_details,
            "expected_annual_ctc": expected_ctc,
            "current_annual_ctc": current_ctc
        }

        profiles.append(profile)
        id_counter += 1


with open("candidate_profiles.json", "w") as f:
    json.dump(profiles, f, indent=2)

print(f"Generated {len(profiles)} profiles in candidate_profiles.json")
