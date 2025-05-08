from supabase import create_client
from django.conf import settings
from functools import lru_cache


@lru_cache(maxsize=1)
def get_supabase_client():
    """
    Returns a cached Supabase client instance.
    The @lru_cache decorator ensures we reuse the same client instance.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
