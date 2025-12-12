from django.db import models
from django.contrib.auth.models import User



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='defolt.jpg', upload_to='profile_pics')
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Text Extraction Data
    extracted_text = models.TextField(blank=True, null=True)
    
    # AI Analysis Results (Stored here after processing)
    ai_status = models.CharField(max_length=20, default='Pending') # Positive/Negative
    ai_score = models.IntegerField(default=0) # 0-100
    ai_confidence = models.FloatField(default=0.0) # 0.0-1.0
    
    def __str__(self):
        return f"{self.file.name} - {self.user.username}"