from rest_framework import serializers
from .models import DocumentTemplate, GeneratedDocument
from django.core.exceptions import ValidationError

class DocumentTemplateSerializer(serializers.ModelSerializer):
    # FIXED: Changed UUIDField to IntegerField to match your new model
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'fields', 'key_field', 'created_at']
        read_only_fields = ['fields', 'created_at']


class DocumentTemplateUploadSerializer(serializers.ModelSerializer):
    """
    Used only for uploading templates.
    'file' is required. fields + key_field are assigned after extract().
    """
    # FIXED: Changed UUIDField to IntegerField
    id = serializers.IntegerField(read_only=True)
    file = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'file', 'key_field']

    def validate_key_field(self, value):
        # Frontend can optionally choose key_field, but validation happens later.
        return value


class GeneratedDocumentSerializer(serializers.ModelSerializer):
    # FIXED: Changed UUIDField to IntegerField
    id = serializers.IntegerField(read_only=True)
    template = serializers.PrimaryKeyRelatedField(queryset=DocumentTemplate.objects.all())

    # We remove HiddenField(CurrentUserDefault) because it crashes with AnonymousUser.
    # We will handle the user assignment manually in the create() method.
    
    class Meta:
        model = GeneratedDocument
        fields = [
            'id',
            'template',
            'created_at',
            'field_values',
            'key_field_value',
            'created_by' 
        ]
        read_only_fields = ['id', 'created_at', 'key_field_value', 'created_by']

    def create(self, validated_data):
        # 1. Safely get the user
        request = self.context.get('request')
        user = None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user

        # 2. Get data
        template = validated_data['template']
        field_values = validated_data['field_values']

        # 3. Derive key field automatically
        key_value = None
        if template.key_field:
            key_value = field_values.get(template.key_field)

        # 4. Create
        return GeneratedDocument.objects.create(
            template=template,
            created_by=user,
            field_values=field_values,
            key_field_value=str(key_value) if key_value else None
        )


class DocumentTemplateUpdateSerializer(serializers.ModelSerializer):
    # File is OPTIONAL here, so you can edit metadata without re-uploading
    file = serializers.FileField(required=False, write_only=True)
    # FIXED: Changed UUIDField to IntegerField
    id = serializers.IntegerField(read_only=True)

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