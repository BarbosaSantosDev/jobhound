from .job_hound_error import JobHoundError


class NoProfileError(JobHoundError):
    def __init__(self) -> None:
        super().__init__(
            "No profile registered yet — register one via POST /api/v1/profiles first"
        )
