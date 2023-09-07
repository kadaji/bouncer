from rest_framework import serializers

from .models import SESEvents


class SESEventsSerializer(serializers.ModelSerializer):
    created_on = serializers.DateTimeField(
        format='%m/%d/%Y',
        input_formats=['%m/%d/%Y %I:%M %p']
    )

    code = serializers.CharField(read_only=True)
    meta_info = serializers.DictField(read_only=True)
    actions = serializers.ListField(read_only=True)

    class Meta:
        model = SESEvents
        fields = '__all__'

        datatables_always_serialize = [
            'meta_info',
            'actions',
            'id',
        ]