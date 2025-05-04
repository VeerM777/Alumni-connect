from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone  # Ensure this is imported
from django.db.models import Q

# Rest of your imports...
from .models import (
    AlumniProfile,
    StudentProfile,
    TeacherProfile,
    Event,
    EventRegistration,
    MentorshipRequest,
    CareerUpdate,
    Notification,
)
from .forms import (
    UserRegisterForm,
    AlumniProfileForm,
    TeacherProfileForm,
    StudentProfileForm,
    ContactForm,
    EventForm,
    MentorshipRequestForm,
    CareerUpdateForm,
)

def home(request):
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by("date")[:5]
    recent_alumni = AlumniProfile.objects.all().order_by("-id")[:5]

    context = {
        "upcoming_events": upcoming_events,
        "recent_alumni": recent_alumni,
        "total_alumni": AlumniProfile.objects.count(),
        "total_events": Event.objects.count(),
    }
    return render(request, "main/home.html", context)

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent!")
            return redirect("home")
    else:
        form = ContactForm()
    return render(request, "main/contact.html", {"form": form})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_type = form.cleaned_data['user_type']
            
            # Authenticate and login the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Account created successfully! Please complete your profile.')
                
                # Redirect to appropriate profile creation
                if user_type == 'alumni':
                    return redirect('alumni_register')
                elif user_type == 'teacher':
                    return redirect('teacher_register')
                else:  # student
                    return redirect('student_register')
            else:
                messages.error(request, 'Authentication failed after registration.')
                return redirect('login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})
def alumni_register(request):
    if not request.user.is_authenticated:
        return redirect('register')
    
    if hasattr(request.user, 'alumniprofile'):
        return redirect('update_alumni_profile')
    
    if request.method == 'POST':
        form = AlumniProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.is_available_for_mentoring = form.cleaned_data.get('is_available_for_mentoring', False)
            profile.save()
            
            messages.success(request, 'Alumni profile created successfully!')
            return redirect('dashboard')
    else:
        form = AlumniProfileForm(initial={
            'is_available_for_mentoring': False,
            'mentoring_preference': 'career_guidance',
            'availability': '1-2'
        })
    
    return render(request, 'registration/alumni_register.html', {
        'form': form,
        'mentor_section': True
    })
def teacher_register(request):
    if not request.user.is_authenticated:
        return redirect('register')
    if hasattr(request.user, 'alumniprofile') or hasattr(request.user, 'teacherprofile') or hasattr(request.user, 'studentprofile'):
        messages.warning(request, "You already have a profile.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.available_for_advising = form.cleaned_data['available_for_advising']
            profile.save()
            messages.success(request, 'Teacher profile created successfully!')
            return redirect('dashboard')
    else:
        form = TeacherProfileForm()
    
    return render(request, 'registration/teacher_register.html', {'form': form})

def student_register(request):
    if not request.user.is_authenticated:
        return redirect('register')
    if hasattr(request.user, 'alumniprofile') or hasattr(request.user, 'teacherprofile') or hasattr(request.user, 'studentprofile'):
        messages.warning(request, "You already have a profile.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Student profile created successfully!')
            return redirect('dashboard')
    else:
        form = StudentProfileForm()
    
    return render(request, 'registration/student_register.html', {'form': form})

@login_required
def create_alumni_profile(request):
    if hasattr(request.user, "alumniprofile"):
        return redirect("update_alumni_profile")

    if request.method == "POST":
        form = AlumniProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Your alumni profile has been created!")
            return redirect("dashboard")
    else:
        form = AlumniProfileForm()

    return render(request, "profiles/create_alumni_profile.html", {"form": form})

@login_required
def create_student_profile(request):
    if hasattr(request.user, "studentprofile"):
        return redirect("update_student_profile")

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Your student profile has been created!")
            return redirect("dashboard")
    else:
        form = StudentProfileForm()

    return render(request, "profiles/create_student_profile.html", {"form": form})

@login_required
def update_alumni_profile(request):
    try:
        profile = request.user.alumniprofile
    except AlumniProfile.DoesNotExist:
        return redirect("create_alumni_profile")

    if request.method == "POST":
        form = AlumniProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("dashboard")
    else:
        form = AlumniProfileForm(instance=profile)

    return render(request, "profiles/update_alumni_profile.html", {"form": form})

@login_required
def update_student_profile(request):
    try:
        profile = request.user.studentprofile
    except StudentProfile.DoesNotExist:
        return redirect("create_student_profile")

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("dashboard")
    else:
        form = StudentProfileForm(instance=profile)

    return render(request, "profiles/update_student_profile.html", {"form": form})

@login_required
def dashboard(request):
    is_alumni = hasattr(request.user, "alumniprofile")
    is_student = hasattr(request.user, "studentprofile")
    is_teacher = hasattr(request.user, "teacherprofile")

    if not (is_alumni or is_student or is_teacher):
        messages.warning(request, "Please complete your profile first.")
        return redirect("home")

    if is_alumni:
        profile = request.user.alumniprofile
        mentorship_requests = MentorshipRequest.objects.filter(
            alumni=request.user, status="pending"
        )
        career_updates = CareerUpdate.objects.filter(alumni=profile).order_by(
            "-start_date"
        )
    elif is_student:
        profile = request.user.studentprofile
        mentorship_requests = MentorshipRequest.objects.filter(student=request.user)
        career_updates = None
    else:  # teacher
        profile = request.user.teacherprofile
        mentorship_requests = None
        career_updates = None

    registered_events = Event.objects.filter(
        eventregistration__user=request.user, date__gte=timezone.now()
    ).order_by("date")

    context = {
        "profile": profile,
        "is_alumni": is_alumni,
        "is_student": is_student,
        "is_teacher": is_teacher,
        "mentorship_requests": mentorship_requests,
        "registered_events": registered_events,
        "career_updates": career_updates,
    }
    return render(request, "dashboard/dashboard.html", context)

@login_required
def create_event(request):
    if not hasattr(request.user, "alumniprofile"):
        messages.error(request, "Only alumni can create events.")
        return redirect("dashboard")

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect("event_detail", event_id=event.id)
    else:
        form = EventForm()

    return render(request, "events/create_event.html", {"form": form})

def event_list(request):
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by("date")
    past_events = Event.objects.filter(date__lt=timezone.now()).order_by("-date")

    context = {"events": upcoming_events, "past_events": past_events}
    return render(request, "events/event_list.html", context)

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    attendees = User.objects.filter(eventregistration__event=event)
    is_registered = False

    if request.user.is_authenticated:
        is_registered = EventRegistration.objects.filter(
            event=event, user=request.user
        ).exists()

    context = {
        "event": event,
        "attendees": attendees,
        "is_registered": is_registered,
    }
    return render(request, "events/event_detail.html", context)

@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, "You are already registered for this event.")
    else:
        EventRegistration.objects.create(event=event, user=request.user)
        messages.success(request, "You have successfully registered for this event!")

    return redirect("event_detail", event_id=event_id)

@login_required
def unregister_from_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    registration = EventRegistration.objects.filter(event=event, user=request.user)
    if registration.exists():
        registration.delete()
        messages.success(request, "You have unregistered from this event.")
    else:
        messages.warning(request, "You are not registered for this event.")

    return redirect("event_detail", event_id=event_id)

@login_required
def add_career_update(request):
    if not hasattr(request.user, "alumniprofile"):
        messages.error(request, "Only alumni can add career updates.")
        return redirect("dashboard")

    if request.method == "POST":
        form = CareerUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.alumni = request.user.alumniprofile
            update.save()
            messages.success(request, "Career update added successfully!")
            return redirect("dashboard")
    else:
        form = CareerUpdateForm()

    return render(request, "career/add_career_update.html", {"form": form})

@login_required
def edit_career_update(request, update_id):
    update = get_object_or_404(CareerUpdate, id=update_id)

    if update.alumni.user != request.user:
        messages.error(request, "You don't have permission to edit this update.")
        return redirect("dashboard")

    if request.method == "POST":
        form = CareerUpdateForm(request.POST, instance=update)
        if form.is_valid():
            form.save()
            messages.success(request, "Career update edited successfully!")
            return redirect("dashboard")
    else:
        form = CareerUpdateForm(instance=update)

    return render(
        request, "career/edit_career_update.html", {"form": form, "update": update}
    )

@login_required
def delete_career_update(request, update_id):
    update = get_object_or_404(CareerUpdate, id=update_id)

    if update.alumni.user != request.user:
        messages.error(request, "You don't have permission to delete this update.")
        return redirect("dashboard")

    if request.method == "POST":
        update.delete()
        messages.success(request, "Career update deleted successfully!")

    return redirect("dashboard")

@login_required
def alumni_list(request):
    alumni = AlumniProfile.objects.filter(is_available_for_mentoring=True)
    return render(request, "mentorship/alumni_list.html", {"alumni": alumni})

@login_required
def request_mentorship(request, alumni_id):
    if not hasattr(request.user, "studentprofile"):
        messages.error(request, "Only students can request mentorship.")
        return redirect("alumni_list")

    alumni_profile = get_object_or_404(AlumniProfile, id=alumni_id)

    if MentorshipRequest.objects.filter(
        student=request.user, alumni=alumni_profile.user
    ).exists():
        messages.warning(
            request, "You have already sent a mentorship request to this alumni."
        )
        return redirect("alumni_list")

    if request.method == "POST":
        form = MentorshipRequestForm(request.POST)
        if form.is_valid():
            mentorship_request = form.save(commit=False)
            mentorship_request.student = request.user
            mentorship_request.alumni = alumni_profile.user
            mentorship_request.save()
            messages.success(request, "Mentorship request sent successfully!")
            return redirect("dashboard")
    else:
        form = MentorshipRequestForm()

    context = {"form": form, "alumni": alumni_profile}

    return render(request, "mentorship/request_mentorship.html", context)

@login_required
def manage_mentorship_requests(request):
    if not hasattr(request.user, "alumniprofile"):
        messages.error(request, "Only alumni can access this page.")
        return redirect("dashboard")

    pending_requests = MentorshipRequest.objects.filter(
        alumni=request.user, status="pending"
    )
    accepted_requests = MentorshipRequest.objects.filter(
        alumni=request.user, status="accepted"
    )
    rejected_requests = MentorshipRequest.objects.filter(
        alumni=request.user, status="rejected"
    )

    context = {
        "pending_requests": pending_requests,
        "accepted_requests": accepted_requests,
        "rejected_requests": rejected_requests,
    }

    return render(request, "mentorship/manage_requests.html", context)

@login_required
def respond_to_mentorship(request, request_id, action):
    if not hasattr(request.user, "alumniprofile"):
        messages.error(request, "Only alumni can respond to mentorship requests.")
        return redirect("dashboard")

    mentorship_request = get_object_or_404(MentorshipRequest, id=request_id)

    if mentorship_request.alumni != request.user:
        messages.error(request, "You don't have permission to respond to this request.")
        return redirect("manage_mentorship_requests")

    if action == "accept":
        mentorship_request.status = "accepted"
        messages.success(request, "Mentorship request accepted!")
    elif action == "reject":
        mentorship_request.status = "rejected"
        messages.success(request, "Mentorship request rejected.")
    else:
        messages.error(request, "Invalid action.")
        return redirect("manage_mentorship_requests")

    mentorship_request.save()
    return redirect("manage_mentorship_requests")

def alumni_directory(request):
    search_query = request.GET.get("search", "")
    grad_year = request.GET.get("graduation_year", "")
    department = request.GET.get("department", "")

    alumni = AlumniProfile.objects.all()

    if search_query:
        alumni = alumni.filter(
            Q(user__username__icontains=search_query)
            | Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(current_company__icontains=search_query)
            | Q(job_title__icontains=search_query)
        )

    if grad_year:
        alumni = alumni.filter(graduation_year=grad_year)

    if department:
        alumni = alumni.filter(department=department)

    graduation_years = (
        AlumniProfile.objects.values_list("graduation_year", flat=True)
        .distinct()
        .order_by("graduation_year")
    )

    departments = (
        AlumniProfile.objects.values_list("department", flat=True)
        .distinct()
        .order_by("department")
    )

    context = {
        "alumni": alumni,
        "search_query": search_query,
        "graduation_years": graduation_years,
        "departments": departments,
        "selected_year": grad_year,
        "selected_department": department,
    }

    return render(request, "directory/alumni_directory.html", context)

@login_required
def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by(
        "-timestamp"
    )
    unread_count = notifications.filter(read=False).count()

    if request.GET.get("mark_all_read") == "true":
        notifications.update(read=True)
        messages.success(request, "All notifications marked as read.")
        return redirect("notifications")

    return render(
        request,
        "notifications/notification_list.html",
        {"notifications": notifications, "unread_count": unread_count},
    )

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification, id=notification_id, recipient=request.user
    )
    notification.read = True
    notification.save()

    if notification.related_link:
        return redirect(notification.related_link)

    return redirect("notifications")

def create_notification(
    recipient, sender, notification_type, title, message, related_link=None
):
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        title=title,
        message=message,
        related_link=related_link,
    )
    return notification

@login_required
def mentorship_dashboard(request):
    upcoming_meetings = []
    active_connections = []
    
    if hasattr(request.user, 'alumniprofile'):
        mentorships = MentorshipRequest.objects.filter(
            alumni=request.user, 
            status='accepted'
        )
        active_connections = [
            request.student.studentprofile for request in mentorships
        ]
    elif hasattr(request.user, 'studentprofile'):
        mentorships = MentorshipRequest.objects.filter(
            student=request.user, 
            status='accepted'
        )
        active_connections = [
            request.alumni.alumniprofile for request in mentorships
        ]
    
    context = {
        'active_connections': active_connections,
        'upcoming_meetings': upcoming_meetings,
    }
    
    return render(request, 'mentorship/mentorship_dashboard.html', context)

def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')