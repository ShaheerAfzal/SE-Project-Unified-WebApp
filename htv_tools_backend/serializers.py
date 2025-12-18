from rest_framework import serializers
from .models import HTVConfiguration

class HTVConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HTVConfiguration
        # Including all fields so the JS can save every setting 
        fields = [
            'id', 'imei', 'apn_name', 'ip_address', 'port', 
            'update_rate', 'can_type', 'pid1', 'pid2', 'pid3', 
            'pid4', 'pid5', 'pid6', 'pid7', 'pid8', 'pid9', 'pid10'
        ]

    def validate_imei(self, value):
        """Custom validation to ensure IMEI is numeric if needed."""
        if not value.isdigit():
            raise serializers.ValidationError("IMEI must be numeric.")
        return value