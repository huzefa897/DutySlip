from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes as drf_permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        profile = getattr(request.user, "profile", None)
        return bool(
            request.user
            and request.user.is_authenticated
            and profile
            and profile.role == "admin"
            and profile.is_active
        )


class IsClient(BasePermission):
    def has_permission(self, request, view):
        profile = getattr(request.user, "profile", None)
        return bool(
            request.user
            and request.user.is_authenticated
            and profile
            and profile.role == "client"
            and profile.is_active
        )


class IsAdminOrReadOnlyClient(BasePermission):
    """Admin: all methods. Client: GET/HEAD/OPTIONS only."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, "profile", None)
        if not profile or not profile.is_active:
            return False
        if profile.role == "admin":
            return True
        return request.method in ("GET", "HEAD", "OPTIONS")


def get_scoped_company_ids(request):
    """
    Returns None  → Admin: no restriction.
    Returns list  → Client: restrict to these company IDs.
    Raises PermissionDenied if unauthenticated or deactivated.
    """
    if not request.user or not request.user.is_authenticated:
        raise PermissionDenied()
    profile = getattr(request.user, "profile", None)
    if not profile or not profile.is_active:
        raise PermissionDenied()
    if profile.role == "admin":
        return None
    return list(profile.companies.values_list("id", flat=True))


def _apply_jwt_auth(fn):
    return authentication_classes([JWTAuthentication])(fn)


def admin_or_client_readonly(fn):
    """Apply IsAdminOrReadOnlyClient + JWTAuthentication to an @api_view function."""
    fn = drf_permission_classes([IsAdminOrReadOnlyClient])(fn)
    fn = _apply_jwt_auth(fn)
    return fn


def admin_only(fn):
    """Apply IsAdmin + JWTAuthentication to an @api_view function."""
    fn = drf_permission_classes([IsAdmin])(fn)
    fn = _apply_jwt_auth(fn)
    return fn


def authenticated_only(fn):
    """Require any authenticated user (admin or client)."""
    from rest_framework.permissions import IsAuthenticated

    fn = drf_permission_classes([IsAuthenticated])(fn)
    fn = _apply_jwt_auth(fn)
    return fn
