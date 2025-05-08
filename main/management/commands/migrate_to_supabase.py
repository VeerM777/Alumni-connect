from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import (
    AlumniProfile, StudentProfile, TeacherProfile, 
    Event, EventRegistration, MentorshipRequest, 
    CareerUpdate, Message, Notification
)
from main.utils.supabase_client import get_supabase_client
import uuid
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Migrates data from SQLite to Supabase'

    def handle(self, *args, **options):
        supabase = get_supabase_client()
        
        # Migrate Users
        self.stdout.write(self.style.SUCCESS('Migrating Users...'))
        users = User.objects.all()
        user_map = {}  # Maps Django user IDs to Supabase UUIDs
        
        for user in users:
            # Generate a UUID for this user
            supabase_id = str(uuid.uuid4())
            user_map[user.id] = supabase_id
            
            try:
                # Create auth user in Supabase
                auth_user = supabase.auth.admin.create_user({
                    'uuid': supabase_id,
                    'email': user.email,
                    'password': 'randompassword123',  # You'll need to reset passwords
                    'email_confirm': True,
                    'user_metadata': {
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                })
                
                # Insert into auth_user table
                supabase.table('auth_user').insert({
                    'id': supabase_id,
                    'username': user.username,
                    'password': user.password,  # This is already hashed
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'is_active': user.is_active,
                    'is_superuser': user.is_superuser,
                    'date_joined': user.date_joined.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }).execute()
                
                self.stdout.write(self.style.SUCCESS(f'✓ Migrated user: {user.username}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Failed to migrate user {user.username}: {str(e)}'))
        
        # Migrate Alumni Profiles
        self.stdout.write(self.style.SUCCESS('Migrating Alumni Profiles...'))
        alumni_profiles = AlumniProfile.objects.all()
        
        for profile in alumni_profiles:
            try:
                if profile.user_id not in user_map:
                    continue
                
                profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
                
                supabase.table('alumni_profile').insert({
                    'user_id': user_map[profile.user_id],
                    'graduation_year': profile.graduation_year,
                    'degree': profile.degree,
                    'department': profile.department,
                    'current_company': profile.current_company,
                    'job_title': profile.job_title,
                    'location': profile.location,
                    'expertise': profile.expertise,
                    'years_of_experience': profile.years_of_experience,
                    'mentoring_preference': profile.mentoring_preference,
                    'availability': profile.availability,
                    'linkedin_profile': profile.linkedin_profile,
                    'bio': profile.bio,
                    'profile_picture_url': profile_picture_url,
                    'is_available_for_mentoring': profile.is_available_for_mentoring
                }).execute()
                
                self.stdout.write(self.style.SUCCESS(f'✓ Migrated alumni profile: {profile.user.username}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Failed to migrate alumni profile {profile.user.username}: {str(e)}'))
        
        # Continue with other models...
        # Similar approach for StudentProfile, TeacherProfile, etc.
        
        # Example for Migrating StudentProfiles
        self.stdout.write(self.style.SUCCESS('Migrating Student Profiles...'))
        student_profiles = StudentProfile.objects.all()
        
        for profile in student_profiles:
            try:
                if profile.user_id not in user_map:
                    continue
                
                profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
                
                supabase.table('student_profile').insert({
                    'user_id': user_map[profile.user_id],
                    'enrollment_year': profile.enrollment_year,
                    'degree_pursuing': profile.degree_pursuing,
                    'department': profile.department,
                    'expected_graduation': profile.expected_graduation,
                    'profile_picture_url': profile_picture_url
                }).execute()
                
                self.stdout.write(self.style.SUCCESS(f'✓ Migrated student profile: {profile.user.username}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Failed to migrate student profile {profile.user.username}: {str(e)}'))
        
        # Note: You'll need to complete the migration for other models similarly
        
        self.stdout.write(self.style.SUCCESS('Migration completed.'))