from django import forms
from .models import Customer, CustomerContact, DESIGNATION_CHOICES
import re
from django.core.exceptions import ValidationError


# 🔹 Tanzania phone number validator
def validate_tz_contact(value):
    pattern = r'^(?:\+255|255|0)?(6[1256789]|7[12345678])[0-9]{7}$'
    if not re.match(pattern, value):
        raise ValidationError("Enter a valid Tanzanian phone number.")


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['designation', 'company_name', 'location', 'email']
        widgets = {
            'designation': forms.Select(
                choices=DESIGNATION_CHOICES,
                attrs={'class': 'form-control'}
            ),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
        }

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')

        # Exclude current instance from uniqueness check if updating
        qs = Customer.objects.filter(company_name__iexact=company_name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("This company name is already registered.")
        return company_name


class CustomerContactForm(forms.ModelForm):
    contact_detail = forms.CharField(
        validators=[validate_tz_contact],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
    )

    class Meta:
        model = CustomerContact
        fields = ['contact_name', 'contact_detail']
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact name'}),
        }
