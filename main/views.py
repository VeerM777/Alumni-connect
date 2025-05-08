from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
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
from main.utils.supabase_client import get_supabase_client
import uuid


def home(request):
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by("date")[
        :5
    ]
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
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            user_type = form.cleaned_data["user_type"]
            first_name = form.cleaned_data.get("first_name", "")
            last_name = form.cleaned_data.get("last_name", "")

            supabase = get_supabase_client()

            try:
                if user_type == "student":
                    # Create Supabase Auth user for student (just like alumni/teachers)
                    signup_data = supabase.auth.sign_up(
                        {
                            "email": email,
                            "password": password,
                            "options": {
                                "data": {
                                    "username": username,
                                    "user_type": user_type,
                                    "first_name": first_name,
                                    "last_name": last_name,
                                }
                            },
                        }
                    )
                    supabase_user_id = signup_data.user.id

                    # Now insert into student_profile with the correct field mapping
                    result = (
                        supabase.table("student_profile")
                        .insert(
                            {
                                "user_id": supabase_user_id,  # Link to the auth user we just created
                                "enrollment_year": form.cleaned_data.get(
                                    "enrollment_year", 2023
                                ),
                                "degree_pursuing": form.cleaned_data.get(
                                    "degree_pursuing", ""
                                ),
                                "department": form.cleaned_data.get("department", ""),
                                "expected_graduation": form.cleaned_data.get(
                                    "expected_graduation", 2027
                                ),
                            }
                        )
                        .execute()
                    )

                    messages.success(request, "Student registration successful!")
                    return redirect("login")
                else:
                    # Create Supabase Auth user for alumni and teachers
                    signup_data = supabase.auth.sign_up(
                        {
                            "email": email,
                            "password": password,
                            "options": {
                                "data": {
                                    "username": username,
                                    "user_type": user_type,
                                    "first_name": first_name,
                                    "last_name": last_name,
                                }
                            },
                        }
                    )
                    supabase_user_id = signup_data.user.id

                    # Insert into respective profile table
                    profile_table = f"{user_type}_profile"
                    supabase.table(profile_table).insert(
                        {
                            "user_id": supabase_user_id,
                            "username": username,
                            "email": email,
                            "first_name": first_name,
                            "last_name": last_name,
                        }
                    ).execute()

                    messages.success(
                        request, f"{user_type.capitalize()} registration successful!"
                    )
                    return redirect("login")

            except Exception as e:
                # Improved error handling
                error_message = str(e)
                if error_message == "{}" or not error_message:
                    if user_type == "student":
                        error_message = "Failed to create student profile. Please check if the email is already registered."
                    else:
                        error_message = "Authentication failed. Please check if the email is already registered or if the password meets the requirements."

                messages.error(request, f"Error during registration: {error_message}")
    else:
        form = UserRegisterForm()

    return render(request, "registration/register.html", {"form": form})


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Please provide both email and password")
            return render(request, "registration/login.html")

        try:
            supabase = get_supabase_client()
            login_response = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            # Store user session data
            request.session["supabase_user_id"] = login_response.user.id
            request.session["user_email"] = email

            messages.success(request, f"Welcome back, {email}!")
            return redirect("dashboard")
        except Exception as e:
            messages.error(request, f"Login failed: {str(e)}")

    return render(request, "registration/login.html")


def logout(request):
    # Clear session
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect("login")


def get_current_user(request):
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return None

    supabase = get_supabase_client()
    response = supabase.table("auth_user").select("*").eq("id", user_id).execute()
    if response.data:
        return response.data[0]
    return None


def alumni_register(request):
    if not request.user.is_authenticated:
        return redirect("register")

    if hasattr(request.user, "alumniprofile"):
        return redirect("update_alumni_profile")

    if request.method == "POST":
        form = AlumniProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.is_available_for_mentoring = form.cleaned_data.get(
                "is_available_for_mentoring", False
            )
            profile.save()

            messages.success(request, "Alumni profile created successfully!")
            return redirect("dashboard")
    else:
        form = AlumniProfileForm(
            initial={
                "is_available_for_mentoring": False,
                "mentoring_preference": "career_guidance",
                "availability": "1-2",
            }
        )

    return render(
        request,
        "registration/alumni_register.html",
        {"form": form, "mentor_section": True},
    )


def teacher_register(request):
    if not request.user.is_authenticated:
        return redirect("register")
    if (
        hasattr(request.user, "alumniprofile")
        or hasattr(request.user, "teacherprofile")
        or hasattr(request.user, "studentprofile")
    ):
        messages.warning(request, "You already have a profile.")
        return redirect("dashboard")

    if request.method == "POST":
        form = TeacherProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.available_for_advising = form.cleaned_data["available_for_advising"]
            profile.save()
            messages.success(request, "Teacher profile created successfully!")
            return redirect("dashboard")
    else:
        form = TeacherProfileForm()

    return render(request, "registration/teacher_register.html", {"form": form})


def student_register(request):
    if not request.user.is_authenticated:
        return redirect("register")
    if (
        hasattr(request.user, "alumniprofile")
        or hasattr(request.user, "teacherprofile")
        or hasattr(request.user, "studentprofile")
    ):
        messages.warning(request, "You already have a profile.")
        return redirect("dashboard")

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Student profile created successfully!")
            return redirect("dashboard")
    else:
        form = StudentProfileForm()

    return render(request, "registration/student_register.html", {"form": form})


@login_required
def create_alumni_profile(request):
    user_id = request.session.get("supabase_user_id")

    if not user_id:
        return redirect("login")

    # Check if profile already exists
    supabase = get_supabase_client()
    profile_check = (
        supabase.table("alumni_profile").select("*").eq("user_id", user_id).execute()
    )

    if profile_check.data:
        return redirect("update_alumni_profile")

    if request.method == "POST":
        form = AlumniProfileForm(request.POST, request.FILES)
        if form.is_valid():
            # Upload profile picture to Supabase Storage if provided
            profile_picture_url = None
            if "profile_picture" in request.FILES:
                profile_pic = request.FILES["profile_picture"]
                file_extension = profile_pic.name.split(".")[-1]
                file_path = f"alumni_profile_pics/{user_id}.{file_extension}"

                # Upload file to Supabase Storage
                file_bytes = profile_pic.read()
                supabase.storage.from_("profile-pictures").upload(file_path, file_bytes)
                profile_picture_url = supabase.storage.from_(
                    "profile-pictures"
                ).get_public_url(file_path)

            # Create alumni profile in Supabase
            cleaned_data = form.cleaned_data
            supabase.table("alumni_profile").insert(
                {
                    "user_id": user_id,
                    "graduation_year": cleaned_data["graduation_year"],
                    "degree": cleaned_data["degree"],
                    "department": cleaned_data["department"],
                    "current_company": cleaned_data["current_company"],
                    "job_title": cleaned_data["job_title"],
                    "location": cleaned_data["location"],
                    "expertise": cleaned_data.get("expertise", ""),
                    "years_of_experience": cleaned_data.get("years_of_experience", 0),
                    "mentoring_preference": cleaned_data.get(
                        "mentoring_preference", ""
                    ),
                    "availability": cleaned_data.get("availability", ""),
                    "linkedin_profile": cleaned_data["linkedin_profile"],
                    "bio": cleaned_data["bio"],
                    "profile_picture_url": profile_picture_url,
                    "is_available_for_mentoring": cleaned_data[
                        "is_available_for_mentoring"
                    ],
                }
            ).execute()

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
    user_id = request.session.get("supabase_user_id")
    supabase = get_supabase_client()

    # Fetch user-specific data
    events = (
        supabase.table("event").select("*").eq("organizer_id", user_id).execute().data
    )
    mentorship_requests = (
        supabase.table("mentorship_request")
        .select("*")
        .eq("student_id", user_id)
        .execute()
        .data
    )

    context = {
        "events": events,
        "mentorship_requests": mentorship_requests,
    }
    return render(request, "dashboard/dashboard.html", context)


@login_required
def create_event(request):
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return redirect("login")

    supabase = get_supabase_client()
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event_data = {
                "title": form.cleaned_data["title"],
                "description": form.cleaned_data["description"],
                "date": form.cleaned_data["date"].isoformat(),
                "location": form.cleaned_data["location"],
                "organizer_id": user_id,
            }
            supabase.table("event").insert(event_data).execute()
            messages.success(request, "Event created successfully!")
            return redirect("dashboard")
    else:
        form = EventForm()

    return render(request, "events/create_event.html", {"form": form})


def event_list(request):
    supabase = get_supabase_client()
    events = (
        supabase.table("event")
        .select("*, auth_user(*)")
        .order("date", desc=False)
        .execute()
    )

    return render(request, "events/event_list.html", {"events": events.data})


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
    user_id = request.session.get("supabase_user_id")
    supabase = get_supabase_client()

    # Check for duplicate registration
    existing_registration = (
        supabase.table("event_registration")
        .select("*")
        .eq("event_id", event_id)
        .eq("user_id", user_id)
        .execute()
        .data
    )
    if existing_registration:
        messages.warning(request, "You are already registered for this event.")
    else:
        supabase.table("event_registration").insert(
            {
                "event_id": event_id,
                "user_id": user_id,
            }
        ).execute()
        messages.success(request, "You have successfully registered for the event!")

    return redirect("dashboard")


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
    student_id = request.session.get("supabase_user_id")
    supabase = get_supabase_client()

    # Check for duplicate mentorship request
    existing_request = (
        supabase.table("mentorship_request")
        .select("*")
        .eq("student_id", student_id)
        .eq("alumni_id", alumni_id)
        .execute()
        .data
    )
    if existing_request:
        messages.warning(
            request, "You have already sent a mentorship request to this alumni."
        )
    else:
        supabase.table("mentorship_request").insert(
            {
                "student_id": student_id,
                "alumni_id": alumni_id,
                "message": request.POST.get("message"),
                "topic": request.POST.get("topic"),
            }
        ).execute()
        messages.success(request, "Mentorship request sent successfully!")

    return redirect("dashboard")


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

    # Build Supabase query
    supabase = get_supabase_client()
    query = supabase.table("alumni_profile").select("*, auth_user(*)")

    # Apply filters
    if search_query:
        query = query.or_(
            f"auth_user.username.ilike.%{search_query}%,auth_user.first_name.ilike.%{search_query}%,auth_user.last_name.ilike.%{search_query}%,current_company.ilike.%{search_query}%,job_title.ilike.%{search_query}%"
        )

    if grad_year:
        query = query.eq("graduation_year", int(grad_year))

    if department:
        query = query.eq("department", department)

    # Execute query
    response = query.execute()

    # Get graduation years and departments for filters
    years_response = (
        supabase.table("alumni_profile").select("graduation_year").execute()
    )
    depts_response = supabase.table("alumni_profile").select("department").execute()

    graduation_years = sorted(
        list(
            {
                year["graduation_year"]
                for year in years_response.data
                if year["graduation_year"]
            }
        )
    )
    departments = sorted(
        list({dept["department"] for dept in depts_response.data if dept["department"]})
    )

    context = {
        "alumni": response.data,
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
    supabase = get_supabase_client()
    supabase.table("notification").update({"read": True}).eq(
        "id", notification_id
    ).execute()
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

    if hasattr(request.user, "alumniprofile"):
        mentorships = MentorshipRequest.objects.filter(
            alumni=request.user, status="accepted"
        )
        active_connections = [request.student.studentprofile for request in mentorships]
    elif hasattr(request.user, "studentprofile"):
        mentorships = MentorshipRequest.objects.filter(
            student=request.user, status="accepted"
        )
        active_connections = [request.alumni.alumniprofile for request in mentorships]

    context = {
        "active_connections": active_connections,
        "upcoming_meetings": upcoming_meetings,
    }

    return render(request, "mentorship/mentorship_dashboard.html", context)


def custom_logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")
