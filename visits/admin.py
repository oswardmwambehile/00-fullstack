from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import *

from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib import admin
from .models import CustomUser


# --- Custom User Creation Form ---
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'first_name', 'last_name', 'company_name',
            'position', 'zone', 'branch', 'contact'
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# --- Custom User Change Form ---
class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'password', 'first_name', 'last_name',
            'company_name', 'position', 'zone', 'branch', 'contact',
            'is_active', 'is_staff', 'is_superuser'
        )

    def clean_password(self):
        return self.initial["password"]


# --- Custom User Admin ---
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        'email', 'first_name', 'last_name', 'company_name',
        'position', 'zone', 'branch', 'contact', 'is_staff', 'is_superuser'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'company_name',
        'position', 'zone', 'branch'
    )
    search_fields = ('email', 'first_name', 'last_name', 'contact')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'contact')}),
        ('Company Info', {'fields': ('company_name',)}),
        ('Job Info', {'fields': ('position', 'zone', 'branch')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'company_name',
                'position', 'zone', 'branch', 'contact',
                'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'
            )}
        ),
    )


# --- Register with admin site ---
admin.site.register(CustomUser, CustomUserAdmin)



from django.contrib import admin
from django.utils.html import format_html
from .models import NewVisit, ProductInterested

# Inline for Products related to a visit
class ProductInterestedInline(admin.TabularInline):
    model = ProductInterested
    extra = 1
    readonly_fields = ("final_order_amount", "payment_collected")
    fields = ("product_interested", "order_estimate", "final_order_amount", "payment_collected")

# Custom Admin for NewVisit
@admin.register(NewVisit)
class NewVisitAdmin(admin.ModelAdmin):
    list_display = (
        "company_name", 
        "contact_person", 
        "meeting_stage_colored", 
        "status_colored", 
        "tag_colored", 
        "created_at", 
        "added_by"
    )
    list_filter = ("meeting_stage", "status", "tag", "created_at", "added_by")
    search_fields = ("company_name__company_name", "contact_person__contact_name", "contact_number")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    inlines = [ProductInterestedInline]
    readonly_fields = ("created_at", "updated_at")

    # Colored badges
    def meeting_stage_colored(self, obj):
        colors = {
            "Prospecting": "#6c757d",       # gray
            "Qualifying": "#0d6efd",        # blue
            "Proposal or Negotiation": "#fd7e14", # orange
            "Closing": "#198754",           # green
            "Payment Followup": "#0d6efd"   # dark blue
        }
        color = colors.get(obj.meeting_stage, "black")
        return format_html(
            '<span style="color:white; background-color:{}; padding:2px 6px; border-radius:4px;">{}</span>',
            color,
            obj.meeting_stage
        )
    meeting_stage_colored.short_description = "Meeting Stage"
    meeting_stage_colored.admin_order_field = "meeting_stage"

    def status_colored(self, obj):
        colors = {
            "Open": "#0dcaf0",           # light blue
            "Won Paid": "#198754",       # green
            "Won Pending Payment": "#fd7e14", # orange
            "Lost": "#dc3545",           # red
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color:white; background-color:{}; padding:2px 6px; border-radius:4px;">{}</span>',
            color,
            obj.status or "Unknown"
        )
    status_colored.short_description = "Status"
    status_colored.admin_order_field = "status"

    def tag_colored(self, obj):
        colors = {
            "Prospect": "#ffc107",  # yellow
            "Lead": "#0d6efd",      # blue
            "Customer": "#198754",  # green
        }
        color = colors.get(obj.tag, "black")
        text_color = "black" if color == "#ffc107" else "white"  # make yellow readable
        return format_html(
            '<span style="color:{}; background-color:{}; padding:2px 6px; border-radius:4px;">{}</span>',
            text_color,
            color,
            obj.tag or "Unknown"
        )
    tag_colored.short_description = "Tag"
    tag_colored.admin_order_field = "tag"
