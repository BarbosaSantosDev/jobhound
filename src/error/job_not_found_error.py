from .job_hound_error import JobHoundError


class JobNotFoundError(JobHoundError):
    def __init__(self, job_id: str):
        super().__init__(f"Job '{job_id}' not found")
        self.job_id = job_id
