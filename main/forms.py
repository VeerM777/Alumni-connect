from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import AlumniProfile, StudentProfile, TeacherProfile, Message, Event, MentorshipRequest, CareerUpdate

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=[
            ('alumni', 'Alumni'),
            ('teacher', 'Teacher'),
            ('student', 'Student')
        ],
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

class AlumniProfileForm(forms.ModelForm):
    is_available_for_mentoring = forms.BooleanField(
        required=False,
        label="Available for Mentoring",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    class Meta:
        model = AlumniProfile
        fields = [
            'graduation_year', 'degree', 'department', 'current_company',
            'job_title', 'location', 'expertise', 'years_of_experience',
            'mentoring_preference', 'availability', 'linkedin_profile',
            'bio', 'profile_picture', 'is_available_for_mentoring'
        ]
        widgets = {
            'graduation_year': forms.NumberInput(attrs={'min': 1900, 'max': timezone.now().year}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = [
            'department', 'position', 'specialization', 'teaching_experience',
            'highest_degree', 'degree_year', 'degree_institution', 'bio',
            'profile_picture', 'available_for_advising'
        ]
        widgets = {
            'position': forms.Select(choices=[
                ('', 'Select your position'),
                ('professor', 'Professor'),
                ('associate_professor', 'Associate Professor'),
                ('assistant_professor', 'Assistant Professor'),
                ('lecturer', 'Lecturer'),
                ('visiting_faculty', 'Visiting Faculty'),
                ('adjunct', 'Adjunct Faculty'),
            ]),
            'highest_degree': forms.Select(choices=[
                ('', 'Select highest degree'),
                ('phd', 'PhD'),
                ('masters', "Master's"),
                ('professional', 'Professional Degree'),
                ('bachelors', "Bachelor's"),
            ]),
            'teaching_experience': forms.NumberInput(attrs={'min': 0}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['enrollment_year', 'degree_pursuing', 'department', 
                 'expected_graduation', 'profile_picture']
        widgets = {
            'enrollment_year': forms.NumberInput(attrs={'min': 2000, 'max': 2025}),
            'expected_graduation': forms.NumberInput(attrs={'min': 2020, 'max': 2035}),
            'degree_pursuing': forms.Select(choices=[
                ('', 'Select your degree'),
                ('bachelors', "Bachelor's"),
                ('masters', "Master's"),
                ('phd', 'PhD'),
            ]),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["name", "email", "content"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Your email address"}),
            "content": forms.Textarea(
                attrs={"rows": 5, "placeholder": "Your message here..."}
            ),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ["organizer", "created_at"]
        widgets = {
            "date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        if self.instance.pk and self.instance.date:
            self.initial["date"] = self.instance.date.strftime("%Y-%m-%dT%H:%M")

class MentorshipRequestForm(forms.ModelForm):
    class Meta:
        model = MentorshipRequest
        fields = ["topic", "message"]
        widgets = {
            "topic": forms.TextInput(
                attrs={"placeholder": "e.g. Career Guidance, Industry Insights, etc."}
            ),
            "message": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Briefly explain your mentorship request..."}
            ),
        }

class CareerUpdateForm(forms.ModelForm):
    class Meta:
        model = CareerUpdate
        exclude = ["alumni"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }