from .job_hound_error import JobHoundError


class ProfileAlreadyExistsError(JobHoundError):
    def __init__(self, slug: str):
        super().__init__(f"Profile '{slug}' already exists")
        self.slug = slug
