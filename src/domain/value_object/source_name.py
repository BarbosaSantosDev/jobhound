from enum import StrEnum


class SourceName(StrEnum):
    """Fontes de vagas que o jobhound sabe farejar."""

    GUPY = "gupy"
    NERDIN = "nerdin"
    REMOTEOK = "remoteok"
