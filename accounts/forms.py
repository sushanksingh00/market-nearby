from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',  # name
            'address',  # bio (reusing existing field)
        ]
        labels = {
            'first_name': 'Name',
            'address': 'Bio',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
