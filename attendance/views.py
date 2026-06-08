from django.utils import timezone
from django.db.models import Count
from accounts.models import User
from projects.models import Project
from attendance.models import Attendance, ActivityLog

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    today = timezone.now().date()
    
    context = {
        'total_users': User.objects.count(),
        'total_projects': Project.objects.count(),
        'today_attendance': Attendance.objects.filter(check_in_time__date=today).count(),
        'recent_activities': ActivityLog.objects.all().order_by('-timestamp')[:10],
        'projects': Project.objects.annotate(checkins=Count('attendance')),
        'today': today,
        'now': timezone.now(),
    }
    return render(request, 'dashboards/admin_dashboard.html', context)