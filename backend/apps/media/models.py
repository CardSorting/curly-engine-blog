from django.db import models
from PIL import Image
import uuid


class Media(models.Model):
    """
    Uploaded images and files
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # File
    file = models.ImageField(upload_to='uploads/%Y/%m/')
    filename = models.CharField(max_length=255)
    alt_text = models.CharField(max_length=255, blank=True)

    # Metadata (auto-filled)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_size = models.IntegerField()  # bytes
    mime_type = models.CharField(max_length=100)

    # Owner
    uploaded_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Media'

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        # Extract image dimensions
        if self.file and not self.width:
            img = Image.open(self.file)
            self.width, self.height = img.size

        # Set file size
        if self.file and not self.file_size:
            self.file_size = self.file.size

        # Set filename if not provided
        if not self.filename:
            self.filename = self.file.name

        super().save(*args, **kwargs)
