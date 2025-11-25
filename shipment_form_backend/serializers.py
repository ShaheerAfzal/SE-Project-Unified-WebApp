# serializers.py
from rest_framework import serializers
from .models import DocumentTemplate, GeneratedDocument


class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = [
            "id",
            "name",
            "file",
            "fields",
            "key_field",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["fields", "created_at", "updated_at"]


class GeneratedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedDocument
        fields = [
            "id",
            "template",
            "field_values",
            "key_field_value",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]
