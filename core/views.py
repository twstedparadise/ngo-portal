from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'field_officer':
        return redirect('field_dashboard')
    elif request.user.role == 'program_manager':
        return redirect('manager_dashboard')
    elif request.user.role == 'finance':
        return redirect('finance_dashboard')
    else:
        return redirect('project_list')