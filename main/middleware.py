from django.shortcuts import redirect
from django.urls import reverse
from main.utils.supabase_client import get_supabase_client
import jwt


class SupabaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Paths that don't require authentication
        public_paths = ["/login/", "/register/", "/password-reset/", "/"]

        # Check if the path requires authentication
        if (
            request.path not in public_paths
            and not request.path.startswith("/static/")
            and not request.path.startswith("/media/")
        ):
            # Get token from session
            token = request.session.get("supabase_access_token")

            if not token:
                return redirect('/login/')  # Use your actual login URL
            # Validate token with Supabase
            try:
                # Decode token without verification to get user ID (Supabase will verify it later)
                decoded = jwt.decode(token, options={"verify_signature": False})
                request.supabase_user_id = decoded.get("sub")

                # Get Supabase client
                supabase = get_supabase_client()

                # This will throw an error if the token is invalid
                user = supabase.auth.get_user(token)
                request.supabase_user = user
            except Exception:
                # Token is invalid or expired
                if "supabase_access_token" in request.session:
                    del request.session["supabase_access_token"]
                if "supabase_user_id" in request.session:
                    del request.session["supabase_user_id"]
                return redirect('/login/')  # Use your actual login URL
        response = self.get_response(request)
        return response
