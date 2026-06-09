from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import auth_views, views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", auth_views.logout_view),
    path("auth/me/", auth_views.me_view),
    path("auth/password-reset/", auth_views.password_reset_request),
    path("auth/password-reset/confirm/", auth_views.password_reset_confirm),
    path("auth/invite/", auth_views.invite_user),
    path("auth/accept-invite/", auth_views.accept_invite),
    path("auth/users/", auth_views.user_list),
    path("auth/users/<int:pk>/", auth_views.user_detail),
    path("auth/users/<int:pk>/companies/", auth_views.user_companies),
    # Companies
    path("companies/", views.company_list, name="company_list"),
    path("companies/<int:pk>/", views.company_detail, name="company_detail"),
    # Company Car Rates
    path(
        "companies/<int:company_id>/rates/",
        views.company_car_rates,
        name="company_car_rates",
    ),
    path(
        "companies/<int:company_id>/rates/<int:car_id>/",
        views.delete_company_car_rate,
        name="delete_company_car_rate",
    ),
    # Company Parties
    path(
        "companies/<int:company_id>/parties/",
        views.company_parties,
        name="company_parties",
    ),
    path(
        "companies/<int:company_id>/invoice-parties/",
        views.company_invoice_parties,
        name="company_invoice_parties",
    ),
    # Cars
    path("cars/", views.car_list, name="car_list"),
    path("cars/<int:pk>/", views.car_detail, name="car_detail"),
    # Trips
    path("trips/", views.trip_list, name="trip_list"),
    path("trips/excel/", views.download_trips_excel, name="download_trips_excel"),
    path("trips/<int:pk>/", views.trip_detail, name="trip_detail"),
    path("trips/<int:pk>/duplicate/", views.duplicate_trip, name="duplicate_trip"),
    # Invoices
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/bulk-excel/", views.bulk_export_excel, name="bulk_export_excel"),
    path(
        "invoices/bulk-pdf/",
        views.bulk_download_invoice_pdf,
        name="bulk_download_invoice_pdf",
    ),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path(
        "invoices/<int:pk>/assign/",
        views.assign_trips_to_invoice,
        name="assign_trips_to_invoice",
    ),
    path(
        "invoices/<int:pk>/remove/<int:trip_id>/",
        views.remove_trip_from_invoice,
        name="remove_trip_from_invoice",
    ),
    path(
        "invoices/<int:pk>/status/",
        views.update_invoice_status,
        name="update_invoice_status",
    ),
    path(
        "invoices/<int:pk>/payment-status/",
        views.update_invoice_payment_status,
        name="update_invoice_payment_status",
    ),
    path(
        "invoices/<int:pk>/pdf/",
        views.download_invoice_pdf,
        name="download_invoice_pdf",
    ),
    path(
        "invoices/<int:pk>/excel/",
        views.download_invoice_excel,
        name="download_invoice_excel",
    ),
    # Business Settings
    path("settings/", views.business_settings, name="business_settings"),
    # Backup and Restore Settings
    path("backup/", views.backup_database),
    path("restore/", views.restore_database),
    path("backup/github/push/", views.push_backup_github),
    path("backup/github/list/", views.list_github_backups),
    path("backup/github/restore/", views.restore_from_github),
]
