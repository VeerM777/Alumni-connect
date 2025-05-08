from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    # Main pages
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    # Authentication
    path("register/", views.register, name="register"),
    path("register/alumni/", views.alumni_register, name="alumni_register"),
    path("register/teacher/", views.teacher_register, name="teacher_register"),
    path("register/student/", views.student_register, name="student_register"),
    path("login/", views.login, name="login"),
    path("logout/", views.custom_logout, name="logout"),
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    # Profile Management
    path(
        "profile/alumni/create/",
        views.create_alumni_profile,
        name="create_alumni_profile",
    ),
    path(
        "profile/alumni/update/",
        views.update_alumni_profile,
        name="update_alumni_profile",
    ),
    path(
        "profile/student/create/",
        views.create_student_profile,
        name="create_student_profile",
    ),
    path(
        "profile/student/update/",
        views.update_student_profile,
        name="update_student_profile",
    ),
    # Event management
    path("events/", views.event_list, name="event_list"),
    path("events/create/", views.create_event, name="create_event"),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path(
        "events/<int:event_id>/register/",
        views.register_for_event,
        name="register_for_event",
    ),
    path(
        "events/<int:event_id>/unregister/",
        views.unregister_from_event,
        name="unregister_from_event",
    ),
    # Career Updates
    path("career/add/", views.add_career_update, name="add_career_update"),
    path(
        "career/<int:update_id>/edit/",
        views.edit_career_update,
        name="edit_career_update",
    ),
    path(
        "career/<int:update_id>/delete/",
        views.delete_career_update,
        name="delete_career_update",
    ),
    # Mentorship
    path("mentorship/alumni/", views.alumni_list, name="alumni_list"),
    path(
        "mentorship/request/<int:alumni_id>/",
        views.request_mentorship,
        name="request_mentorship",
    ),
    path(
        "mentorship/manage/",
        views.manage_mentorship_requests,
        name="manage_mentorship_requests",
    ),
    path(
        "mentorship/<int:request_id>/<str:action>/",
        views.respond_to_mentorship,
        name="respond_to_mentorship",
    ),
    path(
        "mentorship/dashboard/", views.mentorship_dashboard, name="mentorship_dashboard"
    ),
    # Alumni Directory
    path("directory/", views.alumni_directory, name="alumni_directory"),
    # Notifications
    path("notifications/", views.notifications, name="notifications"),
    path(
        "notifications/<int:notification_id>/read/",
        views.mark_notification_read,
        name="mark_notification_read",
    ),
    # Update alumni_list to use Supabase
    path("alumni/", views.alumni_directory, name="alumni_directory"),
]
