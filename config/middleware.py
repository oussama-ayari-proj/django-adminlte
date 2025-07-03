"""
Custom middleware for authentication protection
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class AuthenticationMiddleware:
    """
    Middleware to require authentication for all views except login/logout and admin
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that don't require authentication
        self.exempt_paths = [
            '/accounts/login/',
            '/accounts/logout/',
            '/admin/login/',
            '/admin/logout/',
            '/static/',
            '/media/',
            #'/accounts/password-reset/',
            #'/accounts/register/',
        ]
    
    def __call__(self, request):
        # Print permissions for authenticated users
        if request.user.is_authenticated:
            perms = list(request.user.get_all_permissions())
            print(f"[AUTH] User: {request.user.username} | Permissions: {perms}")
            response = self.get_response(request)
            return response
        else:
            path = request.path_info
            if any(path.startswith(exempt) for exempt in self.exempt_paths):
                response = self.get_response(request)
                return response
            login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')
            return redirect(f'{login_url}?next=/')
