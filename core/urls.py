from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import reminders_api

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Medicines
    path('add-medicine/', views.add_medicine, name='add_medicine'),
    path('medicines/', views.medicines_list, name='medicines_list'),
    path('medicines/<int:pk>/edit/', views.edit_medicine, name='edit_medicine'),
    path('medicines/<int:pk>/delete/', views.delete_medicine, name='delete_medicine'),

    # Reminders
    path('reminders/', views.reminders, name='reminders'),
    path('add-reminder/', views.add_reminder, name='add_reminder'),
    path("reminders/<int:pk>/edit/", views.edit_reminder, name="edit_reminder"),
    path("reminders/<int:pk>/delete/", views.delete_reminder, name="delete_reminder"),

    # Profile & auth
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # Signup / Login / Logout
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Password change (Django auth class-based view)
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name="password_change.html",
        success_url='/profile/'
    ), name='password_change'),

    # Optional: password change done page
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name="password_change_done.html"
    ), name='password_change_done'),

    path("api/reminders/", reminders_api, name="reminders_api"),

    path("api/get-reminders/", views.api_get_reminders),
    path("api/mark-delivered/<int:pk>/", views.api_mark_delivered),

]
