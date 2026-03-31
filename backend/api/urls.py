from django.urls import path
from . import views

urlpatterns = [
    # Companies
    path('companies/', views.company_list),

    # Cars
    path('cars/', views.car_list),

    # Entries
    path('entries/', views.entry_list),
    path('entries/<int:pk>/', views.entry_detail),

    # DutySlips
    path('dutyslips/', views.dutyslip_list),
    path('dutyslips/<int:pk>/', views.dutyslip_detail),
    path('dutyslips/<int:pk>/assign/', views.assign_entries_to_dutyslip),
    path('dutyslips/<int:pk>/remove/<int:entry_id>/', views.remove_entry_from_dutyslip),
]