"""
    Important Link CE URL Configuration
"""
from django.urls import path, include
from rest_framework import routers

from .views import (
    SESEventViewSet,
    index,
    do_bulk_action
)

app_name = 'bouncer'

router = routers.DefaultRouter()
router.register('', SESEventViewSet, basename=app_name)

urlpatterns = [
    path('api/', include(router.urls)),
    
    path('ses_events/', index, name='ses_events'),
    path('ses_events/do_bulk_action', do_bulk_action, name='do_bulk_action'),
    # path('mark_as_read/<uuid:alert_id>', mark_as_read, name='mark_as_read'),
    # path('mark_all_as_read', mark_all_as_read, name='mark_all_as_read'),
    # path('mark_as_unread', mark_as_unread, name='mark_as_unread'),
]
