from django.db import models

import uuid, logging, json
from datetime import datetime
from django.utils import timezone

from django.template import Context, Template
from django.template.loader import get_template
from django.shortcuts import render
from django.http import HttpResponse

from django.conf import settings
from django.db import models

from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from django.template import Context, Template
from django.contrib.auth.models import Group
from django.db.models import JSONField

from cis.models.student import Student
from cis.models.customuser import CustomUser

logger = logging.getLogger(__name__)

class SESEvents(models.Model):

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )

    feedback_id = models.CharField(max_length=100)

    email = models.EmailField()
    created_on = models.DateTimeField(auto_now=False)

    message_subject = models.CharField(blank=True, max_length=5000)
    event_type = models.CharField(max_length=50)

    meta = JSONField(default=dict)

    STATUS_CHOICES = [
        ('new', 'New'),
        ('resolved', 'Resolved'),
    ]
    status = models.CharField(choices=STATUS_CHOICES, max_length=50, default='new')

    def remove_from_donot_send(self):
        from mailer.models import DontSendEntry

        return DontSendEntry.objects.filter(
            to_address=self.email
        ).delete()

    @property
    def is_in_donot_send_list(self):
        from mailer.models import DontSendEntry

        return DontSendEntry.objects.filter(
            to_address=self.email
        ).exists()

    @property
    def actions(self):
        result = []
        if self.status == 'new':
            result.append(
                {
                    'label': 'Mark as Processed',
                    'action': 'mark_as_processed',
                    'icon': 'fa fa-check fas'
                }
            )
        else:
            if self.is_in_donot_send_list:
                result.append(
                    {
                        'label': 'Remove from Do Not Send List',
                        'action': 'remove_from_donot_send',
                        'icon': 'fa fas fa-eraser'
                    }
                )
        return result

    @property
    def meta_info(self):
        user = CustomUser.objects.filter(
            email__iexact=self.email
        )

        if user:
            return user[0].meta_info()
        else:
            student = Student.objects.filter(
                parent_email__iexact=self.email
            )

            if student:
                return {
                    'role': 'parent',
                    'id': str(student[0].id),
                    'ce_url': str(student[0].ce_url)
                }
        return None

    @property
    def code(self):
        return self.meta.get('code')
    
    @classmethod
    def get_or_add(cls, message):
        if SESEvents.objects.filter(
            feedback_id=message.get('id')
        ).exists():
            return SESEvents.objects.get(
                feedback_id=message.get('id')
            )

        created_on = datetime.fromisoformat(message.get('timestamp')[:-1])

        meta = {}

        if message.get('type').lower() == 'bounce':
            meta['code'] = message.get('recipients')[0]['code']
            meta['status'] = message.get('recipients')[0]['status']
        
        record = SESEvents(
            feedback_id=message.get('id'),
            email=message.get('recipients')[0]['emailAddress'],
            message_subject=message.get('subject'),
            event_type=message.get('type'),
            created_on=created_on,
            meta=meta
        )

        record.save()
        return record
    
    def add_mailer_donot_send_entry(self):
        from mailer.models import DontSendEntry

        if DontSendEntry.objects.filter(
            to_address=self.email
        ).exists():
            return self.email

        record = DontSendEntry(
            to_address=self.email,
            when_added=datetime.now()
        )
        record.save()

        return self.email

    @staticmethod
    def format_mesg(mesg):
        obj = {
            'type': ''
        }

        if not mesg.get('eventType'):
            mesg = mesg.get('Message')
            try:
                mesg = json.loads(mesg)
            except Exception as e:
                logger.error(e)
                return None

        obj['type'] = mesg['eventType']
        
        if obj['type'].lower() == 'bounce':
            obj['id'] = mesg['bounce']['feedbackId']
            obj['timestamp'] = mesg['bounce']['timestamp']

            obj['recipients'] = []
            recp = mesg['bounce']['bouncedRecipients']

            for rec in recp:
                recipient = {}
                recipient['emailAddress'] = rec['emailAddress'].lower()
                recipient['action'] = rec['action']
                recipient['status'] = rec['status']
                recipient['code'] = rec.get('diagnosticCode')

                obj['recipients'].append(recipient)
            
            obj['source'] = mesg['mail']['source']
            obj['from'] = mesg['mail']['commonHeaders']['from']
            obj['to'] = mesg['mail']['commonHeaders']['to']
            obj['subject'] = mesg['mail']['commonHeaders']['subject']

            return obj
        elif obj['type'].lower() == 'complaint':
            obj['id'] = mesg['complaint']['feedbackId']
            obj['timestamp'] = mesg['complaint']['timestamp']

            obj['recipients'] = []
            recp = mesg['complaint']['complainedRecipients']

            for rec in recp:
                recipient = {}
                recipient['emailAddress'] = rec['emailAddress'].lower()

                obj['recipients'].append(recipient)
            
            obj['source'] = mesg['mail']['source']
            obj['from'] = mesg['mail']['commonHeaders']['from']
            obj['to'] = mesg['mail']['commonHeaders']['to']
            obj['subject'] = mesg['mail']['commonHeaders']['subject']

            return obj
