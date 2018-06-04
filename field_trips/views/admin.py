from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from field_trips.utils import is_admin
from field_trips.forms import AdminOptionsForm, AdminArchiveForm

@login_required
def admin_index(request):
    """
    Make sure the user is an admin and then present them with an administrative
    overview of the system with edit options.
    """
    if not is_admin(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('field_trips:admin_index')
    else:
        form = AdminOptionsForm()
        archive_form = AdminArchiveForm()
        print(archive_form)
        return render(request, 'field_trips/admin/admin_index.html',
            {'form': form, 'archive_form': archive_form})

def admin_archive(request):
    raise PermissionDenied

def admin_board_report(request):
    raise PermissionDenied
