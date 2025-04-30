from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.conf import settings

def user_passes_test(test_func, login_url=None, redirect_field_name=None):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            
            # If the user is not authenticated, redirect to login page
            if not request.user.is_authenticated:
                path = request.build_absolute_uri()
                resolved_login_url = redirect(login_url or settings.LOGIN_URL)
                # If the login url is the same scheme and net location then just
                # use the path as the "next" url.
                login_scheme, login_netloc = urlparse(resolved_login_url.url)[:2]
                current_scheme, current_netloc = urlparse(path)[:2]
                if (
                    not login_scheme or login_scheme == current_scheme
                ) and (
                    not login_netloc or login_netloc == current_netloc
                ):
                    path = request.get_full_path()
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(
                    path, resolved_login_url.url, redirect_field_name
                )
            else:
                # If the user is authenticated but fails the test, raise PermissionDenied
                raise PermissionDenied
        return _wrapped_view
    return decorator

def admin_required(function=None, redirect_field_name=None, login_url=None):
    """Decorator for views that requires the user to have admin privileges."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.has_admin_privileges,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def team_leader_required(function=None, redirect_field_name=None, login_url=None):
    """Decorator for views that requires the user to be a team leader."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_team_leader,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def department_manager_required(function=None, redirect_field_name=None, login_url=None):
    """Decorator for views that requires the user to be a department manager."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_department_manager,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def senior_manager_required(function=None, redirect_field_name=None, login_url=None):
    """Decorator for views that requires the user to be a senior manager."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_senior_manager,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

# Add other role-specific decorators if needed

