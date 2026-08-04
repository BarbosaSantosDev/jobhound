from .job_hound_error import JobHoundError


class ProfileNotFoundError(JobHoundError):
    def __init__(self, slug: str):
        super().__init__(f"Profile '{slug}' not found")
        self.slug = slug
