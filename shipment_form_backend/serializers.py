# serializers.py
from rest_framework import serializers
from .models import DocumentTemplate, GeneratedDocument
from django.core.exceptions import ValidationError

class DocumentTemplateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'fields', 'key_field', 'created_at']
        read_only_fields = ['fields', 'created_at']


class DocumentTemplateUploadSerializer(serializers.ModelSerializer):
    """
    Used only for uploading templates.
    'file' is required. fields + key_field are assigned after extract().
    """
    id = serializers.UUIDField(read_only=True)
    file = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'file', 'key_field']

    def validate_key_field(self, value):
        # Frontend can optionally choose key_field, but validation happens later.
        return value
class GeneratedDocumentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    template = serializers.PrimaryKeyRelatedField(queryset=DocumentTemplate.objects.all())

    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GeneratedDocument
        fields = [
            'id',
            'template',
            'created_by',
            'created_at',
            'field_values',
            'key_field_value',
        ]
        read_only_fields = ['created_at', 'key_field_value', 'created_by']

    def validate(self, data):
        """
        Ensures that template.key_field exists inside field_values.
        """
        
        template = data.get('template')
        field_values = data.get('field_values') or {}

        if template and template.key_field:
            if template.key_field not in field_values:
                raise serializers.ValidationError({
                    'field_values': f"Missing required key_field '{template.key_field}'"
                })

        return data

    def create(self, validated_data):
        """
        Automatically derive key_field_value and create document entry.
        """
        request = self.context.get('request')
        user = request.user if (request and request.user.is_authenticated) else None
        template = validated_data['template']
        field_values = validated_data['field_values']
        # user = validated_data.get('created_by')

        # derive key field automatically
        key_value = None
        if template.key_field:
            key_value = field_values.get(template.key_field)

        return GeneratedDocument.objects.create(
            template=template,
            created_by=user,
            field_values=field_values,
            key_field_value=str(key_value) if key_value else None
        )


class DocumentTemplateUpdateSerializer(serializers.ModelSerializer):
    # File is OPTIONAL here, so you can edit metadata without re-uploading
    file = serializers.FileField(required=False, write_only=True)

    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'file', 'key_field']
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add the Dynamic Dropdown logic for the "Update" view
        if self.instance:
            # Get keys from the JSON field
            extracted_keys = self.instance.fields.keys()
            field_choices = [(k, k) for k in extracted_keys]
            
            # Set key_field to be a Dropdown (ChoiceField) instead of Text
            self.fields['key_field'] = serializers.ChoiceField(
                choices=field_choices, 
                required=False
            )