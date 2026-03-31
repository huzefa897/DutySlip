from django.urls import path
from . import views

urlpatterns = [
    # Companies
    path('companies/', views.company_list),
    path('companies/<int:pk>/', views.company_detail),

    # Company Car Rates
    path('companies/<int:company_id>/rates/', views.company_car_rates),
    path('companies/<int:company_id>/rates/<int:car_id>/', views.delete_company_car_rate),

    # Cars
    path('cars/', views.car_list),
    path('cars/<int:pk>/', views.car_detail),

    # Entries
    path('entries/', views.entry_list),
    path('entries/<int:pk>/', views.entry_detail),

    # DutySlips
    path('dutyslips/', views.dutyslip_list),
    path('dutyslips/<int:pk>/', views.dutyslip_detail),
    path('dutyslips/<int:pk>/assign/', views.assign_entries_to_dutyslip),
    path('dutyslips/<int:pk>/remove/<int:entry_id>/', views.remove_entry_from_dutyslip),
    path('dutyslips/<int:pk>/status/', views.update_dutyslip_status),

    # Business Settings
    path('settings/', views.business_settings),
    
]