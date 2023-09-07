"""
Cron Views
"""
import csv, io, logging

from django.conf import settings
from django.db import IntegrityError
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.template.loader import get_template, render_to_string


logger = logging.getLogger(__name__)

from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from rest_framework.decorators import api_view 
from rest_framework.response import Response

from cis.utils import CIS_user_only
from cis.menu import draw_menu, cis_menu

# Create your views here.
from .models import SESEvents
from .serializer import SESEventsSerializer

class SESEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SESEventsSerializer
    permission_classes = [CIS_user_only]

    def get_queryset(self):
        records = SESEvents.objects.all()
        return records

def index(request):
    menu = draw_menu(cis_menu, 'users', 'bouncers')
    template = 'bouncer/index.html'
    
    return render(
        request,
        template, {
            'menu': menu,
            'page_title': 'Email Send Errors',
            'api_url': '/ce/bouncer/api/?format=datatables',
        }
    )

def do_bulk_action(request):
    action = request.GET.get('action')

    if request.method == 'POST':
        action = request.POST.get('action')
        
    if action == 'remove_from_donot_send':
        return remove_from_donot_send(request)

    if action == 'mark_as_processed':
        return mark_as_processed(request)

    data = {
        'status': 'success',
        'message': 'invalid action passed',
        'display': 'alert'
    }
    return JsonResponse(data)

def mark_as_processed(request):
    record_id = request.GET.get('record_id')

    record = get_object_or_404(SESEvents, pk=record_id)
    record.status = 'resolved'
    record.save()

    data = {
        'status': 'success',
        'message': 'Success, once the row reload you can if applicable remove the affected email from the do not send list',
        'display': 'alert',
        'action': 'reload_table'
    }
    return JsonResponse(data)

def remove_from_donot_send(request):
    record_id = request.GET.get('record_id')

    record = get_object_or_404(SESEvents, pk=record_id)

    record.remove_from_donot_send()

    data = {
        'status': 'success',
        'message': 'Success',
        'display': 'alert',
        'action': 'reload_table'
    }
    return JsonResponse(data)
