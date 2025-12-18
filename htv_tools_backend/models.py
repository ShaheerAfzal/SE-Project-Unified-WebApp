from django.db import models, migrations

# Create your models here.
class HTVConfiguration(models.Model):
    # IMEI is often used as a unique identifier for trackers [cite: 4, 143]
    imei = models.CharField(max_length=20, unique=True) 
    apn_name = models.CharField(max_length=100, blank=True, null=True) 
    ip_address = models.GenericIPAddressField(blank=True, null=True) 
    port = models.IntegerField(blank=True, null=True) 
    update_rate = models.IntegerField(default=60) 
    
    # CAN Type dropdown options: Standard (STDID) or Extended (EXTID) 
    CAN_TYPE_CHOICES = [
        ('STDID', 'Standard'),
        ('EXTID', 'Extended'),
    ]
    can_type = models.CharField(max_length=10, choices=CAN_TYPE_CHOICES, default='STDID') 

    # Storing 10 PIDs as individual fields for easier mapping to the HTML inputs 
    pid1 = models.CharField(max_length=4, blank=True, null=True) 
    pid2 = models.CharField(max_length=4, blank=True, null=True) 
    pid3 = models.CharField(max_length=4, blank=True, null=True) 
    pid4 = models.CharField(max_length=4, blank=True, null=True) 
    pid5 = models.CharField(max_length=4, blank=True, null=True) 
    pid6 = models.CharField(max_length=4, blank=True, null=True) 
    pid7 = models.CharField(max_length=4, blank=True, null=True) 
    pid8 = models.CharField(max_length=4, blank=True, null=True) 
    pid9 = models.CharField(max_length=4, blank=True, null=True) 
    pid10 = models.CharField(max_length=4, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Config for IMEI: {self.imei}"