from django.contrib import admin
from .models import (
    Message,
    AlumniProfile,
    StudentProfile,
    Event,
    MentorshipRequest,
    CareerUpdate,
    EventRegistration,
    Notification,  # Add this
)

admin.site.register(Message)
admin.site.register(AlumniProfile)
admin.site.register(StudentProfile)
admin.site.register(Event)
admin.site.register(MentorshipRequest)
admin.site.register(CareerUpdate)
admin.site.register(EventRegistration)
admin.site.register(Notification)  # Add this
