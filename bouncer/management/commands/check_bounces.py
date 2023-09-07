import datetime, json, logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.conf import settings
from django.db.utils import IntegrityError
from django.core.management import call_command
from django.contrib.sites.models import Site

from bouncer.models import SESEvents

import boto3
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    '''
    Create groups in DB
    '''
    help = 'Creates user groups in DB'

    # def add_arguments(self, parser):
        # parser.add_argument('-d', '--domain', type=str, help='Fully qualified domain')
        # parser.add_argument('-c', '--campus', type=str, help='Campus')

    def handle(self, *args, **kwargs):
        sqs = boto3.resource("sqs")
        queue = sqs.get_queue_by_name(QueueName=getattr(settings, 'SES_BOUNCE_QUEUE'))

        max_messages = getattr(settings, 'SES_MAX_MESSAGES')
        processed_messages = 0
        per_request = getattr(settings, 'SES_PER_REQUEST')

        while(True):
            messages = queue.receive_messages(MaxNumberOfMessages=5)

            processed_messages += len(messages)
            num_messages = len(messages)

            for message in messages:
                body = message.body

                try:
                    mesg = json.loads(body)

                    obj = SESEvents.format_mesg(mesg)
                    if not obj:
                        ...
                    else:
                        record = SESEvents.get_or_add(obj)
                        if record:
                            record.add_mailer_donot_send_entry()
                            print('Adding to do not entry list')

                    # print(obj)
                    message.delete()

                except Exception as e:
                    print(body)
                    print(e)
                    # logger.error(body)

            if processed_messages >= max_messages:
                print(f'stopping coz exceeded {max_messages}, {processed_messages}')
                return

            if num_messages < per_request:
                print(f'stopping coz only got {num_messages}')
                return