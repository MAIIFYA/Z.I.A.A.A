from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from .models import Team, Department
from accounts.models import User
from accounts.permissions import team_leader_required, department_manager_required, admin_required
from health_cards.models import HealthCheckSession
from votes.models import Vote

@login_required
def team_list(request):
    """View for listing teams"""
    if request.user.is_admin or request.user.is_department_manager:
        # Admins and department managers can see all teams
        teams = Team.objects.all()
    elif request.user.is_senior_manager:
        # Senior managers can see teams in their department
        teams = Team.objects.filter(department__senior_manager=request.user)
    elif request.user.is_team_leader:
        # Team leaders can see their own team
        teams = Team.objects.filter(leader=request.user)
    else:
        # Engineers can see their own team
        if request.user.team:
            teams = Team.objects.filter(id=request.user.team.id)
        else:
            teams = Team.objects.none()
    
    return render(request, 'teams/team_list.html', {'teams': teams})

@login_required
def team_detail(request, team_id):
    """View for team details"""
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user has permission to view this team
    if not (request.user.is_admin or 
            request.user.is_department_manager or 
            (request.user.is_senior_manager and team.department.senior_manager == request.user) or
            (request.user.is_team_leader and team.leader == request.user) or
            (request.user.team and request.user.team.id == team.id)):
        return redirect('team_list')
    
    # Get team members
    members = User.objects.filter(team=team)
    
    # Get recent sessions
    sessions = HealthCheckSession.objects.filter(team=team).order_by('-created_at')[:5]
    
    return render(request, 'teams/team_detail.html', {
        'team': team,
        'members': members,
        'sessions': sessions
    })

@admin_required
def team_create(request):
    """View for creating a new team"""
    if request.method == 'POST':
        name = request.POST.get('name')
        department_id = request.POST.get('department')
        leader_id = request.POST.get('leader')
        
        if name and department_id:
            department = get_object_or_404(Department, id=department_id)
            team = Team.objects.create(name=name, department=department)
            
            if leader_id:
                leader = get_object_or_404(User, id=leader_id)
                team.leader = leader
                team.save()
                
                # Update leader's team and role if needed
                if not leader.is_team_leader:
                    leader.role = 'team_leader'
                leader.team = team
                leader.save()
            
            return redirect('team_detail', team_id=team.id)
    
    departments = Department.objects.all()
    potential_leaders = User.objects.filter(
        Q(role='engineer') | Q(role='team_leader'),
        team__isnull=True
    )
    
    return render(request, 'teams/team_form.html', {
        'departments': departments,
        'potential_leaders': potential_leaders
    })

@admin_required
def team_update(request, team_id):
    """View for updating a team"""
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        department_id = request.POST.get('department')
        leader_id = request.POST.get('leader')
        
        if name and department_id:
            team.name = name
            team.department = get_object_or_404(Department, id=department_id)
            
            # Handle leader change
            if leader_id and (not team.leader or team.leader.id != int(leader_id)):
                # If there was a previous leader, update their role
                if team.leader:
                    old_leader = team.leader
                    old_leader.role = 'engineer'
                    old_leader.save()
                
                # Set new leader
                new_leader = get_object_or_404(User, id=leader_id)
                team.leader = new_leader
                
                # Update new leader's team and role
                if not new_leader.is_team_leader:
                    new_leader.role = 'team_leader'
                new_leader.team = team
                new_leader.save()
            
            team.save()
            return redirect('team_detail', team_id=team.id)
    
    departments = Department.objects.all()
    
    # Get potential leaders (current leader + engineers without a team + engineers in this team)
    potential_leaders = User.objects.filter(
        Q(id=team.leader.id if team.leader else None) |
        Q(role='engineer', team__isnull=True) |
        Q(role='engineer', team=team)
    ).distinct()
    
    return render(request, 'teams/team_form.html', {
        'team': team,
        'departments': departments,
        'potential_leaders': potential_leaders
    })

@admin_required
def team_delete(request, team_id):
    """View for deleting a team"""
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == 'POST':
        # Update team members to have no team
        User.objects.filter(team=team).update(team=None)
        
        # If there's a leader, update their role
        if team.leader:
            leader = team.leader
            leader.role = 'engineer'
            leader.team = None
            leader.save()
        
        team.delete()
        return redirect('team_list')
    
    return render(request, 'teams/team_confirm_delete.html', {'team': team})

@login_required
def department_list(request):
    """View for listing departments"""
    if request.user.is_admin:
        # Admins can see all departments
        departments = Department.objects.all()
    elif request.user.is_department_manager:
        # Department managers can see their own department
        departments = Department.objects.filter(manager=request.user)
    elif request.user.is_senior_manager:
        # Senior managers can see departments they manage
        departments = Department.objects.filter(senior_manager=request.user)
    else:
        # Others can see their own department if they have one
        if request.user.team and request.user.team.department:
            departments = Department.objects.filter(id=request.user.team.department.id)
        else:
            departments = Department.objects.none()
    
    return render(request, 'teams/department_list.html', {'departments': departments})

@login_required
def department_detail(request, department_id):
    """View for department details"""
    department = get_object_or_404(Department, id=department_id)
    
    # Check if user has permission to view this department
    if not (request.user.is_admin or 
            (request.user.is_department_manager and department.manager == request.user) or
            (request.user.is_senior_manager and department.senior_manager == request.user) or
            (request.user.team and request.user.team.department.id == department.id)):
        return redirect('department_list')
    
    # Get teams in this department
    teams = Team.objects.filter(department=department)
    
    # Get department managers
    manager = department.manager
    senior_manager = department.senior_manager
    
    return render(request, 'teams/department_detail.html', {
        'department': department,
        'teams': teams,
        'manager': manager,
        'senior_manager': senior_manager
    })

@admin_required
def department_create(request):
    """View for creating a new department"""
    if request.method == 'POST':
        name = request.POST.get('name')
        manager_id = request.POST.get('manager')
        senior_manager_id = request.POST.get('senior_manager')
        
        if name:
            department = Department.objects.create(name=name)
            
            if manager_id:
                manager = get_object_or_404(User, id=manager_id)
                department.manager = manager
                
                # Update manager's role if needed
                if not manager.is_department_manager:
                    manager.role = 'department_manager'
                    manager.save()
            
            if senior_manager_id:
                senior_manager = get_object_or_404(User, id=senior_manager_id)
                department.senior_manager = senior_manager
                
                # Update senior manager's role if needed
                if not senior_manager.is_senior_manager:
                    senior_manager.role = 'senior_manager'
                    senior_manager.save()
            
            department.save()
            return redirect('department_detail', department_id=department.id)
    
    # Get potential managers (users without department management roles)
    potential_managers = User.objects.filter(
        Q(role='engineer') | Q(role='team_leader')
    )
    
    potential_senior_managers = User.objects.filter(
        Q(role='engineer') | Q(role='team_leader') | Q(role='department_manager')
    )
    
    return render(request, 'teams/department_form.html', {
        'potential_managers': potential_managers,
        'potential_senior_managers': potential_senior_managers
    })

@admin_required
def department_update(request, department_id):
    """View for updating a department"""
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        manager_id = request.POST.get('manager')
        senior_manager_id = request.POST.get('senior_manager')
        
        if name:
            department.name = name
            
            # Handle manager change
            if manager_id and (not department.manager or department.manager.id != int(manager_id)):
                # If there was a previous manager, update their role if they don't manage other departments
                if department.manager:
                    old_manager = department.manager
                    if Department.objects.filter(manager=old_manager).count() <= 1:
                        old_manager.role = 'engineer'
                        old_manager.save()
                
                # Set new manager
                new_manager = get_object_or_404(User, id=manager_id)
                department.manager = new_manager
                
                # Update new manager's role
                if not new_manager.is_department_manager:
                    new_manager.role = 'department_manager'
                    new_manager.save()
            
            # Handle senior manager change
            if senior_manager_id and (not department.senior_manager or department.senior_manager.id != int(senior_manager_id)):
                # If there was a previous senior manager, update their role if they don't manage other departments
                if department.senior_manager:
                    old_senior_manager = department.senior_manager
                    if Department.objects.filter(senior_manager=old_senior_manager).count() <= 1:
                        old_senior_manager.role = 'engineer'
                        old_senior_manager.save()
                
                # Set new senior manager
                new_senior_manager = get_object_or_404(User, id=senior_manager_id)
                department.senior_manager = new_senior_manager
                
                # Update new senior manager's role
                if not new_senior_manager.is_senior_manager:
                    new_senior_manager.role = 'senior_manager'
                    new_senior_manager.save()
            
            department.save()
            return redirect('department_detail', department_id=department.id)
    
    # Get potential managers
    potential_managers = User.objects.filter(
        Q(id=department.manager.id if department.manager else None) |
        Q(role='engineer') | Q(role='team_leader')
    ).distinct()
    
    potential_senior_managers = User.objects.filter(
        Q(id=department.senior_manager.id if department.senior_manager else None) |
        Q(role='engineer') | Q(role='team_leader') | Q(role='department_manager')
    ).distinct()
    
    return render(request, 'teams/department_form.html', {
        'department': department,
        'potential_managers': potential_managers,
        'potential_senior_managers': potential_senior_managers
    })

@admin_required
def department_delete(request, department_id):
    """View for deleting a department"""
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        # Check if there are teams in this department
        if Team.objects.filter(department=department).exists():
            return render(request, 'teams/department_confirm_delete.html', {
                'department': department,
                'error': 'Cannot delete department with existing teams. Please reassign or delete the teams first.'
            })
        
        # If there's a manager, update their role if they don't manage other departments
        if department.manager:
            manager = department.manager
            if Department.objects.filter(manager=manager).count() <= 1:
                manager.role = 'engineer'
                manager.save()
        
        # If there's a senior manager, update their role if they don't manage other departments
        if department.senior_manager:
            senior_manager = department.senior_manager
            if Department.objects.filter(senior_manager=senior_manager).count() <= 1:
                senior_manager.role = 'engineer'
                senior_manager.save()
        
        department.delete()
        return redirect('department_list')
    
    return render(request, 'teams/department_confirm_delete.html', {'department': department})

@login_required
def get_team_members(request, team_id):
    """API view to get team members for a team"""
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user has permission to view this team
    if not (request.user.is_admin or 
            request.user.is_department_manager or 
            (request.user.is_senior_manager and team.department.senior_manager == request.user) or
            (request.user.is_team_leader and team.leader == request.user) or
            (request.user.team and request.user.team.id == team.id)):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    members = User.objects.filter(team=team).values('id', 'username', 'first_name', 'last_name', 'email', 'role')
    return JsonResponse({'members': list(members)})

@login_required
def get_department_teams(request, department_id):
    """API view to get teams for a department"""
    department = get_object_or_404(Department, id=department_id)
    
    # Check if user has permission to view this department
    if not (request.user.is_admin or 
            (request.user.is_department_manager and department.manager == request.user) or
            (request.user.is_senior_manager and department.senior_manager == request.user) or
            (request.user.team and request.user.team.department.id == department.id)):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    teams = Team.objects.filter(department=department).values('id', 'name')
    return JsonResponse({'teams': list(teams)})
