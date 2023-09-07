from django.contrib import admin

# Register your models here.
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from bouncer.models import SESEvents

@admin.register(SESEvents)
class SESEventsAdmin(admin.ModelAdmin):
    list_display = (
        'created_on', 'event_type', 'id', 'email', 'message_subject', 
    )

    # fields = [
    #     # 'id',
    #     'email',
    #     'message_subject'
    # ]
