import json
from vespa.application import Vespa

# Connect to Vespa instance
vespa_app = Vespa(url="http://localhost", port=8080)

# Example jobs data (you can load from a file instead)
with open("jobs.json", "r") as f:
    jobs = json.load(f)
# Feed jobs to Vespa
for job in jobs:
    response = vespa_app.feed_data_point(
        schema="job",  # <-- make sure your Vespa schema is called "jobs"
        data_id=job["job_id"],  # use job_id as the document ID
        fields=job
    )
    print(f"Fed {job['job_id']} -> status: {response.status_code}, response: {response.get_json()}")
