# serializers.py
from rest_framework import serializers
from .models import DocumentTemplate, GeneratedDocument
from django.core.exceptions import ValidationError

class DocumentTemplateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'fields', 'key_field', 'is_active', 'created_at']
        read_only_fields = ['fields', 'is_active', 'created_at']

class DocumentTemplateUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading templates.
    Accepts file and optional key_field (frontend chooses it).
    After save, view calls extract_and_populate_fields().
    """
    id = serializers.UUIDField(read_only=True)
    file = serializers.FileField(write_only=True)

    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'file', 'key_field']

    def validate_key_field(self, value):
        # validation will be deferred until fields are extracted.
        # Accept None here; view will run extract_and_populate_fields() immediately after create.
        return value

class GeneratedDocumentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    template = serializers.PrimaryKeyRelatedField(queryset=DocumentTemplate.objects.filter(is_active=True))
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GeneratedDocument
        fields = ['id', 'template', 'created_by', 'created_at', 'field_values', 'key_field_value']
        read_only_fields = ['created_at', 'key_field_value', 'created_by']

    def validate(self, data):
        """
        Validate that required template.key_field exists in field_values.
        """
        template = data.get('template')
        field_values = data.get('field_values') or {}
        if template and template.key_field:
            if template.key_field not in field_values:
                raise serializers.ValidationError({
                    'field_values': f"key_field '{template.key_field}' must be present in field_values."
                })
        return data

    def create(self, validated_data):
        """
        Automatically set key_field_value from template.key_field and save created_by.
        """
        user = validated_data.get('created_by')
        template = validated_data.get('template')
        field_values = validated_data.get('field_values', {})

        key_value = None
        if template and template.key_field:
            key_value = field_values.get(template.key_field)

        gen = GeneratedDocument.objects.create(
            template=template,
            created_by=user,
            field_values=field_values,
            key_field_value=str(key_value) if key_value is not None else None
        )
        return gen
