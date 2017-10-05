import os

from django.shortcuts import render
#TODO from django.conf import settings - settings.MEDIA_ROOT - вот как конфиг можно юзать
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from msw.models import Attachments, Filters, Accounts
from django.views.generic.edit import CreateView, UpdateView
from msw.forms import AddFilterForm, EditFilterForm, AddAccountForm, EditAccountForm
from django.db.models import Count
from django.conf import settings

def attachments(request):
    exts = Attachments.objects.values('ext').annotate(cnt=Count('ext'))
    return render(request, "attachments.html", {'exts': exts})

def attachments_list(request, ext):
    return render(request, "attachments-list.html", {'ext':ext})

def index(request):
    return render(request, "index.html", {})

def del_filter(request, id):
    Filters.objects.filter(id=id).delete()
    return HttpResponseRedirect('/msw/filters-finds/')

def del_account(request, id):
    Accounts.objects.filter(id=id).delete()
    return HttpResponseRedirect('/msw/accounts/')

def accounts_errors(request, account_id):
    return render(request, "accounts-errors.html", {"account_id": account_id})

def mailbox(request):
    """
    Test action
    :param request: HttpRequest
    :return:
    """

    return render(request, "mailbox.html", {})

def accounts(request):
    """

    :param request: HttpRequest
    :return:
    """
    return render(request, "accounts.html", {})

def filters_finds(request):
    """

    :param request: HttpRequest
    :return:
    """
    return render(request, "filter_finds.html", {})

class AddFilterForm(CreateView):
    form_class = AddFilterForm
    model = Filters
    template_name = "add_filter.html"
    success_url = '/msw/filters-finds/'

class EditFilterForm(UpdateView):
    form_class = EditFilterForm
    model = Filters
    template_name = "edit_filter.html"
    success_url = '/msw/filters-finds/'

class AddAccountForm(CreateView):
    form_class = AddAccountForm
    model = Accounts
    template_name = "add_account.html"
    success_url = '/msw/accounts/'

class EditAccountForm(UpdateView):
    form_class = EditAccountForm
    model = Accounts
    template_name = "edit_account.html"
    success_url = '/msw/accounts/'

def download(request, id):
    attachment = Attachments.objects.get(id=id)
    file_path = os.path.join(settings.ATTACHMENTS_PATH, attachment.hash)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = 'attachment; filename=' + attachment.file_name
            return response
    raise Http404
