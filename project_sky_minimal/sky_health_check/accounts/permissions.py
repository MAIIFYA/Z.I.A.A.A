from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class EngineerRequiredMixin(UserPassesTestMixin):
    """
    Mixin to require user to be an engineer
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_engineer

class TeamLeaderRequiredMixin(UserPassesTestMixin):
    """
    Mixin to require user to be a team leader
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_team_leader

class SeniorManagerRequiredMixin(UserPassesTestMixin):
    """
    Mixin to require user to be a senior manager
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_senior_manager

class DepartmentManagerRequiredMixin(UserPassesTestMixin):
    """
    Mixin to require user to be a department manager
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_department_manager

class AdminRequiredMixin(UserPassesTestMixin):
    """
    Mixin to require user to be an admin
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin

def engineer_required(view_func):
    """
    Decorator for views that checks if the user is an engineer
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_engineer:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper

def team_leader_required(view_func):
    """
    Decorator for views that checks if the user is a team leader
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_team_leader:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper

def senior_manager_required(view_func):
    """
    Decorator for views that checks if the user is a senior manager
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_senior_manager:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper

def department_manager_required(view_func):
    """
    Decorator for views that checks if the user is a department manager
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_department_manager:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper

def admin_required(view_func):
    """
    Decorator for views that checks if the user is an admin
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper
