from django.urls import path
from . import views

urlpatterns = [
    # Companies
    path("companies/", views.company_list),
    path("companies/<int:pk>/", views.company_detail),
    # Company Car Rates
    path("companies/<int:company_id>/rates/", views.company_car_rates),
    path(
        "companies/<int:company_id>/rates/<int:car_id>/", views.delete_company_car_rate
    ),
    # Company Parties
    path("companies/<int:company_id>/parties/", views.company_parties),
    # Cars
    path("cars/", views.car_list),
    path("cars/<int:pk>/", views.car_detail),
    # Trips
    path("trips/", views.trip_list),
    path("trips/excel/", views.download_trips_excel),
    path("trips/<int:pk>/", views.trip_detail),
    path("trips/<int:pk>/duplicate/", views.duplicate_trip),
    # Invoices
    path("invoices/", views.invoice_list),
    path("invoices/bulk-excel/", views.bulk_export_excel),
    path("invoices/bulk-pdf/", views.bulk_download_invoice_pdf),
    path("invoices/<int:pk>/", views.invoice_detail),
    path("invoices/<int:pk>/assign/", views.assign_trips_to_invoice),
    path("invoices/<int:pk>/remove/<int:trip_id>/", views.remove_trip_from_invoice),
    path("invoices/<int:pk>/status/", views.update_invoice_status),
    path("invoices/<int:pk>/payment-status/", views.update_invoice_payment_status),
    path("invoices/<int:pk>/pdf/", views.download_invoice_pdf),
    path("invoices/<int:pk>/excel/", views.download_invoice_excel),
    # Business Settings
    path("settings/", views.business_settings),
    # Backup and Restore Settings
    path("backup/", views.backup_database),
    path("restore/", views.restore_database),
    path("backup/github/push/", views.push_backup_github),
    path("backup/github/list/", views.list_github_backups),
    path("backup/github/restore/", views.restore_from_github),
]
