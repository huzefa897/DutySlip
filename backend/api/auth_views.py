from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Company, InvitationToken, UserProfile
from .permissions import IsAdmin


# ── Login / Refresh / Logout ──────────────────────────────────────────────────

# Login is handled by simplejwt's TokenObtainPairView wired in urls.py.
# Refresh is handled by simplejwt's TokenRefreshView wired in urls.py.


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get("refresh")
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass
    return Response({"detail": "Logged out."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    profile = getattr(user, "profile", None)
    return Response(
        {
            "id": user.id,
            "email": user.email,
            "name": user.get_full_name() or user.username,
            "role": profile.role if profile else None,
            "is_active": profile.is_active if profile else False,
            "companies": list(profile.companies.values("id", "name"))
            if profile
            else [],
        }
    )


# ── Password Reset ────────────────────────────────────────────────────────────


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request):
    email = request.data.get("email", "").lower().strip()
    try:
        user = User.objects.get(email__iexact=email)
        token_obj = InvitationToken.make(
            email=user.email, purpose="password_reset", hours=1
        )
        reset_url = f"{settings.FRONTEND_URL}/auth/reset-password/confirm?token={token_obj.token}"
        send_mail(
            subject="DutySlip — Password Reset",
            message=f"Reset your password by visiting:\n{reset_url}\n\nThis link expires in 1 hour.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except User.DoesNotExist:
        pass
    # Always return 200 — never reveal whether the email exists
    return Response({"detail": "If that email exists, a reset link has been sent."})


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    token_str = request.data.get("token", "")
    new_password = request.data.get("password", "")
    if not token_str or not new_password:
        return Response({"error": "token and password are required."}, status=400)
    try:
        token_obj = InvitationToken.objects.get(
            token=token_str, purpose="password_reset"
        )
    except InvitationToken.DoesNotExist:
        return Response({"error": "Invalid token."}, status=400)
    if not token_obj.is_valid():
        return Response({"error": "Token expired or already used."}, status=400)
    try:
        user = User.objects.get(email__iexact=token_obj.email)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=400)
    user.set_password(new_password)
    user.save()
    token_obj.used = True
    token_obj.save()
    return Response({"detail": "Password updated. You can now log in."})


# ── Invite + Accept ───────────────────────────────────────────────────────────


@api_view(["POST"])
@permission_classes([IsAdmin])
def invite_user(request):
    email = request.data.get("email", "").lower().strip()
    role = request.data.get("role", "client")
    if not email:
        return Response({"error": "email is required."}, status=400)
    if role not in ("admin", "client"):
        return Response({"error": "role must be 'admin' or 'client'."}, status=400)
    if User.objects.filter(email__iexact=email).exists():
        return Response({"error": "A user with that email already exists."}, status=400)
    token_obj = InvitationToken.make(
        email=email, purpose="invite", role=role, created_by=request.user, hours=48
    )
    setup_url = f"{settings.FRONTEND_URL}/auth/accept-invite?token={token_obj.token}"
    send_mail(
        subject="You're invited to DutySlip",
        message=f"Set up your account by visiting:\n{setup_url}\n\nThis link expires in 48 hours.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
    return Response({"detail": f"Invitation sent to {email}."}, status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
def accept_invite(request):
    token_str = request.data.get("token", "")
    password = request.data.get("password", "")
    name = request.data.get("name", "").strip()
    if not token_str or not password:
        return Response({"error": "token and password are required."}, status=400)
    try:
        token_obj = InvitationToken.objects.get(token=token_str, purpose="invite")
    except InvitationToken.DoesNotExist:
        return Response({"error": "Invalid token."}, status=400)
    if not token_obj.is_valid():
        return Response({"error": "Token expired or already used."}, status=400)
    if User.objects.filter(email__iexact=token_obj.email).exists():
        return Response(
            {"error": "An account with this email already exists."}, status=400
        )
    parts = name.split(" ", 1)
    user = User.objects.create_user(
        username=token_obj.email,
        email=token_obj.email,
        password=password,
        first_name=parts[0] if parts else "",
        last_name=parts[1] if len(parts) > 1 else "",
    )
    UserProfile.objects.create(user=user, role=token_obj.role)
    token_obj.used = True
    token_obj.save()
    return Response({"detail": "Account created. You can now log in."}, status=201)


# ── User Management (Admin only) ──────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAdmin])
def user_list(request):
    profiles = (
        UserProfile.objects.select_related("user").prefetch_related("companies").all()
    )
    data = []
    for p in profiles:
        data.append(
            {
                "id": p.user.id,
                "email": p.user.email,
                "name": p.user.get_full_name() or p.user.username,
                "role": p.role,
                "is_active": p.is_active,
                "companies": list(p.companies.values("id", "name")),
                "date_joined": p.user.date_joined,
            }
        )
    return Response(data)


@api_view(["PATCH"])
@permission_classes([IsAdmin])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
        profile = user.profile
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return Response({"error": "User not found."}, status=404)

    if "role" in request.data:
        role = request.data["role"]
        if role not in ("admin", "client"):
            return Response({"error": "role must be 'admin' or 'client'."}, status=400)
        profile.role = role

    if "is_active" in request.data:
        profile.is_active = bool(request.data["is_active"])

    if "name" in request.data:
        parts = request.data["name"].strip().split(" ", 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ""
        user.save(update_fields=["first_name", "last_name"])

    profile.save()
    return Response(
        {
            "id": user.id,
            "email": user.email,
            "name": user.get_full_name() or user.username,
            "role": profile.role,
            "is_active": profile.is_active,
            "companies": list(profile.companies.values("id", "name")),
        }
    )


@api_view(["PUT"])
@permission_classes([IsAdmin])
def user_companies(request, pk):
    """Replace the full set of companies assigned to a Client user."""
    try:
        user = User.objects.get(pk=pk)
        profile = user.profile
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return Response({"error": "User not found."}, status=404)

    company_ids = request.data.get("company_ids", [])
    if not isinstance(company_ids, list):
        return Response({"error": "company_ids must be a list."}, status=400)

    companies = Company.objects.filter(id__in=company_ids)
    profile.companies.set(companies)
    return Response(
        {
            "id": user.id,
            "companies": list(profile.companies.values("id", "name")),
        }
    )
