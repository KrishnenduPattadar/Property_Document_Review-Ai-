
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Document, Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required for password reset.")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'phone']
        widget = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('file',)
        # ADD THIS: Makes the input look good (Bootstrap) and filters file dialog
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control', 
                'accept': '.pdf,.docx,.jpg,.jpeg,.png'
            }),
        }

    # KEEP THIS: Actual security check
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'docx', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError("Only PDF, DOCX, JPG, and PNG files are allowed.")
        return file
    