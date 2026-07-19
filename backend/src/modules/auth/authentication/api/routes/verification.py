"""
Exposes HTTP endpoints for the email verification flow.
Handles validating the 6-digit OTP sent via email and allowing users to request a new OTP if it expired.
"""

from fastapi import APIRouter, Request, Response

from src.modules.auth.authentication.api.dependencies.project import (
    OptionalProjectIdDep,
)
from src.modules.auth.authentication.api.dependencies.use_cases import (
    LocalResendVerificationUseCaseDep,
    LocalVerifyEmailUseCaseDep,
)
from src.modules.auth.authentication.api.schemas import (
    MessageResponse,
    RegisterResponse,
    RequestNewVerificationEmail,
    VerifyEmailRequest,
)
from src.shared.api.dependencies import UnitOfWorkDeps, IsChallengedDep
from src.shared.api.utils import extract_client_metadata, set_refresh_token_cookie

router = APIRouter()


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    request: Request,
    response: Response,
    req: VerifyEmailRequest,
    uow: UnitOfWorkDeps,
    usecase: LocalVerifyEmailUseCaseDep,
    is_challenged: IsChallengedDep,
    project_id: OptionalProjectIdDep,
):
    """
    Verify a user's email address using a 6-digit OTP.

    This endpoint accepts the email address and the 6-digit One Time Password (OTP) that was emailed to the user upon registration.
    - If the OTP matches and hasn't expired (5-minute window), the user is permanently created in the database and marked as verified.
    - Once verified, the user can proceed to the `/login/local` endpoint.

    **Returns:**
    A success message upon successful verification.
    """
    client_meta = extract_client_metadata(request)
    async with uow:
        user, refresh_token = await usecase.execute(
            uow,
            req.email,
            req.otp,
            project_id=project_id,
            is_challenged=is_challenged,
            turnstile_token=req.turnstile_token,
            client_meta=client_meta,
        )
    set_refresh_token_cookie(response, refresh_token)
    return MessageResponse(message="Email verified successfully")


@router.post("/verify-email/resend", response_model=RegisterResponse)
async def resend_verification(
    request: Request,
    req: RequestNewVerificationEmail,
    uow: UnitOfWorkDeps,
    usecase: LocalResendVerificationUseCaseDep,
    is_challenged: IsChallengedDep,
    project_id: OptionalProjectIdDep,
):
    """
    Resend the 6-digit verification OTP.

    If the user's previous OTP expired or they didn't receive the email, this endpoint generates a fresh 6-digit OTP and extends the verification window for another 5 minutes.
    The new OTP is sent to the user's email address.

    **Returns:**
    A generic success message.
    """
    client_meta = extract_client_metadata(request)
    async with uow:
        expires_in = await usecase.execute(
            uow,
            req.email,
            project_id=project_id,
            is_challenged=is_challenged,
            turnstile_token=req.turnstile_token,
            client_meta=client_meta,
        )
    return RegisterResponse(
        message="If the email is registered and unverified, a new OTP has been sent.",
        expires_in_seconds=expires_in,
    )
