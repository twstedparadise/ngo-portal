import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from .models import Attendance, ActivityLog
from projects.models import Project
from accounts.models import User
from .utils import haversine_distance_m as haversine_distance

@login_required
def field_dashboard(request):
    """Dashboard for field officers showing assigned projects"""
    if request.user.role != 'field_officer':
        messages.error(request, 'Access denied. Field officer access required.')
        return redirect('home')
    
    # Get projects assigned to this officer
    assigned_projects = request.user.assigned_projects.all()
    
    # Get today's active attendance (checked in but not out)
    today = timezone.now().date()
    active_attendance = Attendance.objects.filter(
        user=request.user,
        check_in_time__date=today,
        check_out_time__isnull=True
    ).first()
    
    context = {
        'projects': assigned_projects,
        'active_attendance': active_attendance,
        'today': today,
    }
    
    return render(request, 'dashboards/field_dashboard.html', context)

@login_required
def admin_dashboard(request):
    """Dashboard for admin users with system overview"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin access required.')
        return redirect('home')
    
    today = timezone.now().date()
    
    context = {
        'total_users': User.objects.count(),
        'total_projects': Project.objects.count(),
        'today_attendance': Attendance.objects.filter(check_in_time__date=today).count(),
        'today': today,
        'now': timezone.now(),
    }
    
    return render(request, 'dashboards/admin_dashboard.html', context)

@login_required
def manager_dashboard(request):
    """Dashboard for program managers"""
    if request.user.role != 'program_manager':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    today = timezone.now().date()
    week_ago = today - timezone.timedelta(days=7)
    
    projects = Project.objects.annotate(
        total_checkins=Count('attendance'),
        unique_officers=Count('attendance__user', distinct=True)
    )
    
    context = {
        'total_projects': projects.count(),
        'total_checkins': Attendance.objects.count(),
        'weekly_checkins': Attendance.objects.filter(check_in_time__date__gte=week_ago).count(),
        'active_officers': User.objects.filter(
            role='field_officer',
            attendance__check_in_time__date__gte=week_ago
        ).distinct().count(),
        'projects': projects[:10],
        'today': today,
    }
    
    return render(request, 'dashboards/manager_dashboard.html', context)

@login_required
def finance_dashboard(request):
    """Dashboard for finance officers"""
    if request.user.role != 'finance':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    today = timezone.now().date()
    month_ago = today - timezone.timedelta(days=30)
    
    # Get recent activities for the table
    recent_activities = ActivityLog.objects.select_related('user', 'project').order_by('-timestamp')[:15]
    
    context = {
        'total_attendance_hours': 1247,  # Placeholder - calculate from actual data later
        'active_projects': Project.objects.count(),
        'monthly_checkins': Attendance.objects.filter(check_in_time__date__gte=month_ago).count(),
        'unique_officers': User.objects.filter(role='field_officer').count(),
        'recent_activities': recent_activities,
        'today': today,
    }
    
    return render(request, 'dashboards/finance_dashboard.html', context)

@login_required
def attendance_logs(request):
    """View all attendance logs"""
    records = Attendance.objects.select_related('user', 'project').all().order_by('-check_in_time')
    return render(request, 'attendance/attendance_logs.html', {'attendance_records': records})

@login_required
def check_in(request, project_id):
    """Handle GPS check-in with geofence validation"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    project = get_object_or_404(Project, id=project_id)
    
    try:
        data = json.loads(request.body)
        user_lat = float(data.get('latitude'))
        user_lng = float(data.get('longitude'))
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'error': 'Invalid GPS data'}, status=400)
    
    # Calculate distance to project center
    distance = haversine_distance(
        user_lat, user_lng,
        project.latitude, project.longitude
    )
    
    # Check if within geofence
    if distance <= project.radius_m:
        attendance = Attendance.objects.create(
            user=request.user,
            project=project,
            check_in_time=timezone.now(),
            check_in_latitude=user_lat,
            check_in_longitude=user_lng,
            is_within_geofence=True
        )
        
        ActivityLog.objects.create(
            user=request.user,
            action='check_in',
            project=project,
            latitude=user_lat,
            longitude=user_lng,
            within_geofence=True,
            details=f"Check-in successful. Distance: {distance:.2f}m"
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Check-in successful! Distance: {distance:.0f}m',
            'attendance_id': attendance.id
        })
    else:
        ActivityLog.objects.create(
            user=request.user,
            action='check_in_failed',
            project=project,
            latitude=user_lat,
            longitude=user_lng,
            within_geofence=False,
            details=f"Geofence violation. Distance: {distance:.2f}m (Max: {project.radius_m}m)"
        )
        
        return JsonResponse({
            'success': False,
            'error': f'You are {distance:.0f}m away. Must be within {project.radius_m}m.'
        }, status=403)

@login_required
def check_out(request, attendance_id):
    """Handle GPS check-out"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    attendance = get_object_or_404(Attendance, id=attendance_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        user_lat = float(data.get('latitude'))
        user_lng = float(data.get('longitude'))
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'error': 'Invalid GPS data'}, status=400)
    
    attendance.check_out_time = timezone.now()
    attendance.check_out_latitude = user_lat
    attendance.check_out_longitude = user_lng
    
    duration = attendance.check_out_time - attendance.check_in_time
    attendance.duration_minutes = int(duration.total_seconds() / 60)
    attendance.save()
    
    ActivityLog.objects.create(
        user=request.user,
        action='check_out',
        project=attendance.project,
        latitude=user_lat,
        longitude=user_lng,
        within_geofence=True,
        details=f"Checked out after {attendance.duration_minutes} minutes"
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Check-out successful! Duration: {attendance.duration_minutes} minutes.',
        'duration': attendance.duration_minutes
    })