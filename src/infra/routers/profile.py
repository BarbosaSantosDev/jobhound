from fastapi import APIRouter, Depends, status

from src.app.usecase import (
    GetProfile,
    RegisterProfile,
    RegisterProfileInput,
    UpdateProfile,
    UpdateProfileInput,
)
from src.infra.routers.dependencies import (
    get_profile_usecase,
    get_register_profile_usecase,
    get_update_profile_usecase,
)
from src.infra.routers.schemas import ProfileSchema, ProfileWriteSchema

router = APIRouter(prefix="/api/v1/profiles", tags=["profile"])


@router.post("", response_model=ProfileSchema, status_code=status.HTTP_201_CREATED)
async def register_profile(
    body: ProfileWriteSchema,
    use_case: RegisterProfile = Depends(get_register_profile_usecase),
) -> ProfileSchema:
    profile = await use_case.execute(
        RegisterProfileInput(
            name=body.name,
            headline=body.headline,
            seniority=body.seniority,
            primary_stack=body.primary_stack,
            secondary_stack=body.secondary_stack,
            preferred_locations=body.preferred_locations,
            accepts_remote=body.accepts_remote,
            summary=body.summary,
        )
    )
    return ProfileSchema.from_domain(profile)


@router.get("/{slug}", response_model=ProfileSchema)
async def get_profile(
    slug: str,
    use_case: GetProfile = Depends(get_profile_usecase),
) -> ProfileSchema:
    return ProfileSchema.from_domain(await use_case.execute(slug))


@router.put("/{slug}", response_model=ProfileSchema)
async def update_profile(
    slug: str,
    body: ProfileWriteSchema,
    use_case: UpdateProfile = Depends(get_update_profile_usecase),
) -> ProfileSchema:
    profile = await use_case.execute(
        UpdateProfileInput(
            slug=slug,
            name=body.name,
            headline=body.headline,
            seniority=body.seniority,
            primary_stack=body.primary_stack,
            secondary_stack=body.secondary_stack,
            preferred_locations=body.preferred_locations,
            accepts_remote=body.accepts_remote,
            summary=body.summary,
        )
    )
    return ProfileSchema.from_domain(profile)
