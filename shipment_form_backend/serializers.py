# serializers.py
from rest_framework import serializers
from .models import DocumentTemplate, GeneratedDocument

class DocumentTemplateSerializer(serializers.ModelSerializer):
    generated_documents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'file', 'fields', 'key_field', 'created_at', 'updated_at', 'is_active', 'generated_documents_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'fields', 'generated_documents_count']
    
    def get_generated_documents_count(self, obj):
        return obj.generated_documents.count()

class DocumentTemplateUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = ['name', 'file', 'key_field']

class GeneratedDocumentSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneratedDocument
        fields = ['id', 'template', 'template_name', 'document_name', 'created_by', 'created_by_name', 
                 'created_at', 'field_values', 'key_field_value', 'generated_file', 'download_url']
        read_only_fields = ['id', 'created_at', 'created_by']
    
    def get_download_url(self, obj):
        if obj.generated_file:
            return obj.generated_file.url
        return None

class DocumentGenerationSerializer(serializers.Serializer):
    template_id = serializers.UUIDField()
    document_name = serializers.CharField(max_length=255, required=False, default="Generated Document")
    field_values = serializers.JSONField()
    
    def create(self, validated_data):
        request = self.context.get('request')
        template_id = validated_data['template_id']
        field_values = validated_data['field_values']
        document_name = validated_data.get('document_name', 'Generated Document')
        
        try:
            template = DocumentTemplate.objects.get(id=template_id, is_active=True)
        except DocumentTemplate.DoesNotExist:
            raise serializers.ValidationError("Template not found")
        
        # Create generated document
        generated_doc = GeneratedDocument.objects.create(
            template=template,
            document_name=document_name,
            field_values=field_values,
            created_by=request.user if request and request.user.is_authenticated else None,
            key_field_value=field_values.get(template.key_field, '')
        )
        
        # Generate and attach the file
        generated_doc.generate_and_attach_file()
        
        return generated_doc