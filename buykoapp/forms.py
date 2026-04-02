from django import forms
from .models import Product
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'category', 'quantity', 'image']   # 👈 Added quantity








from django import forms
from .models import Banner

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'image']












# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class RegisterForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    mobile = forms.CharField(max_length=15)
    gender = forms.ChoiceField(choices=(("male","Male"),("female","Female"),("other","Other")))
    address = forms.CharField(widget=forms.Textarea(attrs={"rows":3}))
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        email = cleaned_data.get("email")

        # Password check
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")

        # Email duplicate check
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered!")

        return cleaned_data








from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['mobile', 'gender', 'address']
        widgets = {
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }






# buykoapp/forms.py
from django import forms
from django.contrib.auth.models import User

from django import forms

class OTPForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    
class VerifyOTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

class ResetPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    otp = forms.CharField(max_length=6, widget=forms.HiddenInput())
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("new_password") != cleaned.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match")
        return cleaned
