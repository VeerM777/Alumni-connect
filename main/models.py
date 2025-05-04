from django.db import models
from django.contrib.auth.models import User

class AlumniProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    graduation_year = models.IntegerField(null=True, blank=True, default=None)
    degree = models.CharField(max_length=100, blank=True, default='')
    department = models.CharField(max_length=100, blank=True, default='')
    current_company = models.CharField(max_length=200, blank=True, default='')
    job_title = models.CharField(max_length=100, blank=True, default='')
    location = models.CharField(max_length=100, blank=True, null=True)
    expertise = models.CharField(max_length=200, blank=True, default='')
    years_of_experience = models.IntegerField(null=True, blank=True, default=0)
    mentoring_preference = models.CharField(max_length=50, blank=True, default='')
    availability = models.CharField(max_length=10, blank=True, default='')
    linkedin_profile = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    profile_picture = models.ImageField(upload_to="profile_pics", blank=True, null=True)
    is_available_for_mentoring = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.graduation_year or 'No Year'}"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enrollment_year = models.IntegerField(null=True, blank=True)
    degree_pursuing = models.CharField(max_length=100, blank=True, default='')
    department = models.CharField(max_length=100, blank=True, default='')
    expected_graduation = models.IntegerField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pics", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.enrollment_year or 'No Year'}"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True, default='')
    position = models.CharField(max_length=50, blank=True, default='')
    specialization = models.CharField(max_length=200, blank=True, default='')
    teaching_experience = models.IntegerField(null=True, blank=True, default=0)
    highest_degree = models.CharField(max_length=50, blank=True, default='')
    degree_year = models.IntegerField(null=True, blank=True)
    degree_institution = models.CharField(max_length=200, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    profile_picture = models.ImageField(upload_to="profile_pics", blank=True, null=True)
    available_for_advising = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.position or 'No Position'}"

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["event", "user"]

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class MentorshipRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="mentorship_requests_sent"
    )
    alumni = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="mentorship_requests_received"
    )
    message = models.TextField()
    topic = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mentorship: {self.student.username} → {self.alumni.username}"

class CareerUpdate(models.Model):
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.alumni.user.username} - {self.title} at {self.company}"

class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('mentorship_request', 'Mentorship Request'),
        ('mentorship_response', 'Mentorship Response'),
        ('event_reminder', 'Event Reminder'),
        ('new_message', 'New Message'),
        ('career_update', 'Career Update'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="sent_notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    related_link = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username} from {self.sender.username if self.sender else 'System'}"
    
    class Meta:
        ordering = ['-timestamp']