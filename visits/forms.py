from decimal import Decimal, ROUND_HALF_UP
from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from .models import NewVisit, ProductInterested, Customer, CustomerContact


# --------------------------
# Step 1: Add New Visit (Client Info + Discussion + Location)
# --------------------------
class NewVisitForm(forms.ModelForm):
    contact_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly", "id": "id_contact_number"})
    )
    designation = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly", "id": "id_designation"})
    )

    class Meta:
        model = NewVisit
        fields = [
            "company_name",
            "contact_person",
            "contact_number",
            "designation",
            "latitude",
            "longitude",
            "item_discussed",
        ]
        widgets = {
            "company_name": forms.Select(attrs={"class": "form-select", "id": "id_company_name"}),
            "contact_person": forms.Select(attrs={"class": "form-select", "id": "id_contact_person"}),
            "item_discussed": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "latitude": forms.HiddenInput(attrs={"id": "id_latitude"}),
            "longitude": forms.HiddenInput(attrs={"id": "id_longitude"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["company_name"].queryset = Customer.objects.all().order_by("company_name")
        self.fields["contact_person"].queryset = CustomerContact.objects.none()
        self.fields["contact_person"].empty_label = "Select company first"

        company_id = None
        if self.data.get("company_name"):
            try:
                company_id = int(self.data.get("company_name"))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and getattr(self.instance, "company_name_id", None):
            company_id = self.instance.company_name_id

        if company_id:
            self.fields["contact_person"].queryset = CustomerContact.objects.filter(
                customer_id=company_id
            ).order_by("contact_name")
            self.fields["contact_person"].empty_label = "Select contact"

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("latitude")
        lon = cleaned.get("longitude")

        if not lat or not lon:
            raise ValidationError("Location not detected. Allow location access and wait for the map.")

        try:
            cleaned["latitude"] = str(
                Decimal(str(lat)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
            )
            cleaned["longitude"] = str(
                Decimal(str(lon)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
            )
        except Exception:
            raise ValidationError("Invalid coordinates received. Please refresh and try again.")

        return cleaned


# --------------------------
# Step 2: Products Interested (Add only)
# --------------------------
class ProductInterestedForm(forms.ModelForm):
    class Meta:
        model = ProductInterested
        fields = ["product_interested"]
        widgets = {"product_interested": forms.Select(attrs={"class": "form-select"})}


ProductInterestedFormSet = modelformset_factory(
    ProductInterested,
    form=ProductInterestedForm,
    extra=1,
    can_delete=True,
)


# --------------------------
# Update Visit Form (Stage Dependent)
# --------------------------
class UpdateVisitForm(forms.ModelForm):
    class Meta:
        model = NewVisit
        exclude = ["added_by", "created_at", "updated_at"]
        widgets = {
            "company_name": forms.Select(attrs={"class": "form-select"}),
            "contact_person": forms.Select(attrs={"class": "form-select"}),
            "contact_number": forms.TextInput(attrs={"class": "form-control"}),
            "designation": forms.TextInput(attrs={"class": "form-control"}),
            "latitude": forms.HiddenInput(attrs={"id": "id_latitude"}),
            "longitude": forms.HiddenInput(attrs={"id": "id_longitude"}),
            "meeting_stage": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "tag": forms.Select(attrs={"class": "form-select"}),
            "item_discussed": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "client_budget": forms.NumberInput(attrs={"class": "form-control"}),
            "is_order_final": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "contract_outcome": forms.Select(attrs={"class": "form-select"}),
            "contract_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "reason_lost": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "is_payment_collected": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, stage=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Stage-dependent logic
        for f in ("is_order_final", "contract_outcome", "contract_amount", "reason_lost", "is_payment_collected"):
            if f in self.fields:
                self.fields[f].required = False
                self.fields[f].widget.attrs.pop("hidden", None)

        # Proposal / Negotiation
        if stage == "Proposal or Negotiation":
            self.fields["is_order_final"].widget = forms.CheckboxInput(attrs={"class": "form-check-input"})

        # Closing
        elif stage == "Closing":
            self.fields["contract_outcome"].widget = forms.Select(attrs={"class": "form-select"})
            self.fields["contract_outcome"].choices = [("Won", "Won"), ("Lost", "Lost")]
            self.fields["contract_outcome"].required = True

            if self.instance.contract_outcome == "Won":
                self.fields["contract_amount"].widget = forms.NumberInput(attrs={"class": "form-control"})
                self.fields["is_payment_collected"].widget = forms.CheckboxInput(attrs={"class": "form-check-input"})
            elif self.instance.contract_outcome == "Lost":
                self.fields["reason_lost"].widget = forms.Textarea(attrs={"class": "form-control", "rows": 2})

        # Payment Followup (optional)
        elif stage == "Payment Followup":
            self.fields["is_payment_collected"].widget = forms.CheckboxInput(attrs={"class": "form-check-input"})


# --------------------------
# Update Product Interested Form
# --------------------------
class UpdateProductInterestedForm(forms.ModelForm):
    class Meta:
        model = ProductInterested
        exclude = ["visit"]
        widgets = {
            "product_interested": forms.Select(attrs={"class": "form-select"}),
            "order_estimate": forms.NumberInput(attrs={"class": "form-control field-order_estimate"}),
            "final_order_amount": forms.NumberInput(attrs={"class": "form-control field-final_order_amount"}),
            "payment_collected": forms.NumberInput(attrs={"class": "form-control field-payment_collected"}),  # ✅ always NumberInput
        }

    def __init__(self, *args, stage=None, contract_outcome=None, **kwargs):
        super().__init__(*args, **kwargs)

        for f in ("order_estimate", "final_order_amount", "payment_collected"):
            if f in self.fields:
                self.fields[f].required = False

        if stage == "Proposal or Negotiation":
            if "order_estimate" in self.fields:
                self.fields["order_estimate"].required = True

        elif stage == "Closing":
            if contract_outcome == "Won":
                if "final_order_amount" in self.fields:
                    self.fields["final_order_amount"].required = True
                # ❌ Do NOT touch payment_collected here; hide it via JS instead
                if "payment_collected" in self.fields:
                    self.fields["payment_collected"].widget = forms.NumberInput(
                        attrs={"class": "form-control field-payment_collected"}
                    )
            elif contract_outcome == "Lost":
                if "final_order_amount" in self.fields:
                    self.fields["final_order_amount"].widget = forms.HiddenInput()
                if "payment_collected" in self.fields:
                    self.fields["payment_collected"].widget = forms.HiddenInput()

        elif stage == "Payment Followup":
            if "payment_collected" in self.fields:
                self.fields["payment_collected"].required = True
                self.fields["payment_collected"].widget = forms.NumberInput(
                    attrs={"class": "form-control field-payment_collected"}
                )


UpdateProductInterestedFormSet = modelformset_factory(
    ProductInterested,
    form=UpdateProductInterestedForm,
    extra=1,
    can_delete=True,
)
