from django.db import models
from django.utils import timezone

DESIGNATION_CHOICES = [
    ('Owner', 'Owner'),
    ('Engineer', 'Engineer'),
    ('Contractor', 'Contractor'),
]

class Customer(models.Model):
    designation = models.CharField(
        max_length=100,
        choices=DESIGNATION_CHOICES  # 🔽 Make dropdown
    )
    company_name = models.CharField(
        max_length=200,
        unique=True  # 🛑 Prevent duplicates
    )
    location = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.company_name


class CustomerContact(models.Model):
    customer = models.ForeignKey(Customer, related_name="contacts", on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=150)
    contact_detail = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.contact_name} ({self.customer.company_name})"
