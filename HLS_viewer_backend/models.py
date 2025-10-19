from django.db import models

# Create your models here.


class Stream(models.Model):
    name = models.CharField(max_length=100, help_text="Display name for the stream")
    url = models.URLField(help_text="HLS stream URL (.m3u8)")
    description = models.TextField(blank=True, null=True, help_text="Optional stream info")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
