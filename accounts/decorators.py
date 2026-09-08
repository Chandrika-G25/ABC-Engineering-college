from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles=[]):
    """
    Decorator for views that checks whether a user has a specific role assigned.
    If the user is a superuser, access is granted automatically.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please login to access this page.")
                return redirect('accounts:login')
            
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, "Access Denied: You do not have permission to access this resource.")
            return redirect('core:home')
        return _wrapped_view
    return decorator

def super_admin_required(view_func):
    return role_required(['SUPER_ADMIN'])(view_func)

def admin_required(view_func):
    return role_required(['SUPER_ADMIN', 'ADMIN'])(view_func)

def teacher_required(view_func):
    return role_required(['TEACHER'])(view_func)

def student_required(view_func):
    return role_required(['STUDENT'])(view_func)
