from django.shortcuts import render

from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .forms import CustomerForm, CustomerContactForm
from .models import Customer, CustomerContact

# Use a plain ModelFormSet for adding contacts
ContactFormSet = modelformset_factory(
    CustomerContact,
    form=CustomerContactForm,
    extra=1,          # at least one empty row
    can_delete=True
)

def add_customer(request):
    if request.method == "POST":
        customer_form = CustomerForm(request.POST)
        # IMPORTANT: use the SAME prefix for GET and POST
        formset = ContactFormSet(request.POST, queryset=CustomerContact.objects.none(), prefix="contacts")

        if customer_form.is_valid() and formset.is_valid():
            # Save parent first
            customer = customer_form.save()

            # Save contacts and attach the customer
            contacts = formset.save(commit=False)
            for c in contacts:
                c.customer = customer
                c.save()

            # Handle deletes (if any were added then removed)
            for obj in formset.deleted_objects:
                obj.delete()

            return redirect("customer_list")

    else:
        customer_form = CustomerForm()
        # Same prefix in GET; start with no contacts from DB
        formset = ContactFormSet(queryset=CustomerContact.objects.none(), prefix="contacts")

    return render(request, "users/add_customer.html", {
        "customer_form": customer_form,
        "formset": formset,
        "is_update": False,   # just for your heading/buttons
    })


from django.shortcuts import render
from django.db.models import Q
from .models import Customer
from visits.models import NewVisit  # import the visit model

from django.shortcuts import render
from django.db.models import Q
from customer.models import Customer
from visits.models import NewVisit

from django.db.models import Q
from django.shortcuts import render
from customer.models import Customer
from visits.models import NewVisit

def customer_list(request):
    query = request.GET.get("q", "")
    customers = Customer.objects.prefetch_related("visits").all()

    if query:
        customers = customers.filter(
            Q(company_name__icontains=query) |
            Q(designation__icontains=query)
        )

    for customer in customers:
        latest_visit = customer.visits.order_by('-created_at').first()
        customer.latest_tag = latest_visit.tag if latest_visit and latest_visit.tag else None

    customers = customers.order_by('-created_at')

    context = {
        "customers": customers,
        "query": query,
    }
    return render(request, "users/customer_list.html", context)




def admincustomer_list(request):
    query = request.GET.get("q", "")
    customers = Customer.objects.prefetch_related("contacts").all()

    if query:
        customers = customers.filter(
            Q(company_name__icontains=query) |
            Q(designation__icontains=query)
        )

    customers = customers.order_by('-created_at')  # 👈 order by latest created

    context = {
        "customers": customers,
        "query": query,
    }
    return render(request, "company/customer_list.html", context)


from django.shortcuts import render, get_object_or_404, redirect
from django.forms import inlineformset_factory
from django.contrib import messages
from .models import Customer, CustomerContact
from .forms import CustomerForm, CustomerContactForm


def update_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    # Inline formset for contacts tied to customer
    ContactFormSet = inlineformset_factory(
        Customer,
        CustomerContact,
        form=CustomerContactForm,
        extra=0,          # no blank rows by default
        can_delete=True   # allow delete
    )

    if request.method == "POST":
        customer_form = CustomerForm(request.POST, instance=customer)
        formset = ContactFormSet(request.POST, instance=customer)

        if customer_form.is_valid() and formset.is_valid():
            customer_form.save()
            formset.save()  # updates, deletes, and adds new
            messages.success(request, "✅ Customer updated successfully!")
            return redirect("customer_list")
        else:
            print("❌ FORM ERRORS:", customer_form.errors, formset.errors)
    else:
        customer_form = CustomerForm(instance=customer)
        formset = ContactFormSet(instance=customer)

    return render(request, "users/update_customer.html", {
        "customer_form": customer_form,
        "formset": formset,
        "customer": customer,
    })

def adminupdate_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    # Inline formset for contacts tied to customer
    ContactFormSet = inlineformset_factory(
        Customer,
        CustomerContact,
        form=CustomerContactForm,
        extra=0,          # no blank rows by default
        can_delete=True   # allow delete
    )

    if request.method == "POST":
        customer_form = CustomerForm(request.POST, instance=customer)
        formset = ContactFormSet(request.POST, instance=customer)

        if customer_form.is_valid() and formset.is_valid():
            customer_form.save()
            formset.save()  # updates, deletes, and adds new
            messages.success(request, "✅ Customer updated successfully!")
            return redirect("customers_list")
        else:
            print("❌ FORM ERRORS:", customer_form.errors, formset.errors)
    else:
        customer_form = CustomerForm(instance=customer)
        formset = ContactFormSet(instance=customer)

    return render(request, "company/update_customer.html", {
        "customer_form": customer_form,
        "formset": formset,
        "customer": customer,
    })

# ✅ DELETE CUSTOMER
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        customer.delete()
        messages.success(request, "🗑️ Customer deleted successfully!")
        return redirect("customer_list")

    return render(request, "users/customer_confirm_delete.html", {"customer": customer})



# ✅ DELETE CUSTOMER
def admindelete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        customer.delete()
        messages.success(request, "🗑️ Customer deleted successfully!")
        return redirect("customers_list")

    return render(request, "company/customer_confirm_delete.html", {"customer": customer})

from django.shortcuts import render, get_object_or_404
from visits.models import CustomUser
from django.db.models import Q  # 🔍 For OR lookups

def user_list(request):
    query = request.GET.get('q', '')
    users = CustomUser.objects.all().order_by('-date_joined')  # order by newest first

    if query:
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(company_name__icontains=query)  # <-- added this
        ).order_by('-date_joined')  # maintain ordering after filtering

    return render(request, 'company/user_list.html', {
        'users': users,
        'query': query,
    })

from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Sum
from customer.models import Customer
from visits.models import NewVisit, ProductInterested

User = get_user_model()

def index(request):
    # General counts
    total_customers = Customer.objects.count() or 0
    total_users = User.objects.count() or 0
    total_new_visits = NewVisit.objects.count() or 0

    # Orders
    total_orders_new_visit = ProductInterested.objects.filter(
        final_order_amount__isnull=False
    ).count() or 0

    total_order_amount = ProductInterested.objects.aggregate(
        total=Sum("final_order_amount")
    )["total"] or 0

    # Payment collected
    total_payment_collected = ProductInterested.objects.aggregate(
        total=Sum("payment_collected")
    )["total"] or 0

    # Stage-wise visits
    total_prospecting_visits = NewVisit.objects.filter(meeting_stage="Prospecting").count() or 0
    total_qualifying_visits = NewVisit.objects.filter(meeting_stage="Qualifying").count() or 0
    total_proposal_visits = NewVisit.objects.filter(meeting_stage="Proposal or Negotiation").count() or 0
    total_closing_visits = NewVisit.objects.filter(meeting_stage="Closing").count() or 0

    # ✅ Payment Follow-up Visits
    total_payment_followup_visits = NewVisit.objects.filter(
        products__payment_collected__gt=0
    ).distinct().count() or 0

    context = {
        "total_customers": total_customers,
        "total_users": total_users,
        "total_new_visits": total_new_visits,
        "total_orders_new_visit": total_orders_new_visit,
        "total_order_amount": total_order_amount,
        "total_payment_collected": total_payment_collected,
        "total_prospecting_visits": total_prospecting_visits,
        "total_qualifying_visits": total_qualifying_visits,
        "total_proposal_visits": total_proposal_visits,
        "total_closing_visits": total_closing_visits,
        "total_payment_followup_visits": total_payment_followup_visits,
    }

    return render(request, "company/index.html", context)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from visits.models import CustomUser

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if user == request.user:
        message = "You can't change your own status."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': message}, status=403)
        messages.error(request, message)
        return redirect('user_list')

    if user.is_superuser:
        message = "You can't change status of a superuser."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': message}, status=403)
        messages.error(request, message)
        return redirect('user_list')

    user.is_active = not user.is_active
    user.save()

    status = "enabled" if user.is_active else "disabled"
    message = f"User {user.email} has been {status}."

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'is_active': user.is_active})

    messages.success(request, message)
    return redirect('user_list')

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from visits.models import CustomUser

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.company_name = request.POST.get("company_name")
        user.position = request.POST.get("position")
        user.zone = request.POST.get("zone")
        user.branch = request.POST.get("branch")
        user.contact = request.POST.get("contact")
        user.save()

        messages.success(request, "User updated successfully.")
        return redirect("user_list")

    return render(request, "company/edit_user.html", {"user_obj": user})


from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from visits.models import NewVisit, ProductInterested, CustomUser


def user_detail(request, user_id):
    # Get the user
    user = get_object_or_404(CustomUser, id=user_id)

    # All visits added by this user
    new_visits = NewVisit.objects.filter(
        added_by=user
    ).select_related('company_name', 'contact_person').prefetch_related('products')

    # Prepare combined visits (if you want a timeline later)
    combined_visits = list(new_visits.order_by('-created_at'))

    # ✅ Summary metrics
    total_new_visits = new_visits.count()

    total_orders = ProductInterested.objects.filter(
        visit__added_by=user,
        final_order_amount__isnull=False
    ).count()

    total_order_amount = ProductInterested.objects.filter(
        visit__added_by=user,
        final_order_amount__isnull=False
    ).aggregate(total=Sum('final_order_amount'))['total'] or 0

    total_payments = ProductInterested.objects.filter(
        visit__added_by=user,
        payment_collected__isnull=False
    ).aggregate(total=Sum('payment_collected'))['total'] or 0

    context = {
        'user': user,
        'combined_visits': combined_visits,

        # summary cards
        'total_new_visits': total_new_visits,
        'total_orders': total_orders,
        'total_order_amount': total_order_amount,
        'total_payments': total_payments,
    }

    return render(request, 'company/user_detail.html', context)




from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from visits.models import ProductInterested, NewVisit

def product_detail(request, pk):
    visit = get_object_or_404(NewVisit, pk=pk)
    products_interested = visit.products.all()

    totals = products_interested.aggregate(
        total_final_order=Sum("final_order_amount"),
        total_payment_collected=Sum("payment_collected"),
    )

    return render(request, "company/product_detail.html", {
        "visit": visit,
        "products_interested": products_interested,
        "total_final_order": totals["total_final_order"] or 0,
        "total_payment_collected": totals["total_payment_collected"] or 0,
    })


def customerproduct_detail(request, pk):
    visit = get_object_or_404(NewVisit, pk=pk)
    products_interested = visit.products.all()

    totals = products_interested.aggregate(
        total_final_order=Sum("final_order_amount"),
        total_payment_collected=Sum("payment_collected"),
    )

    return render(request, "users/product_detail.html", {
        "visit": visit,
        "products_interested": products_interested,
        "total_final_order": totals["total_final_order"] or 0,
        "total_payment_collected": totals["total_payment_collected"] or 0,
    })


def admincustomerproduct_detail(request, pk):
    visit = get_object_or_404(NewVisit, pk=pk)
    products_interested = visit.products.all()

    totals = products_interested.aggregate(
        total_final_order=Sum("final_order_amount"),
        total_payment_collected=Sum("payment_collected"),
    )

    return render(request, "company/adminproduct_detail.html", {
        "visit": visit,
        "products_interested": products_interested,
        "total_final_order": totals["total_final_order"] or 0,
        "total_payment_collected": totals["total_payment_collected"] or 0,
    })



from django.shortcuts import get_object_or_404, render
from .models import Customer, CustomerContact
from visits.models import NewVisit

def view_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    contacts = CustomerContact.objects.filter(customer=customer)

    # ✅ Fetch only visits for this customer
    new_visits = (
        NewVisit.objects.filter(company_name=customer)
        .select_related("added_by", "contact_person")
        .order_by("-created_at")  # latest first
    )

    return render(request, "users/customer_detail.html", {
        "customer": customer,
        "contacts": contacts,
        "visits": new_visits,   # changed to just visits
    })

def adminview_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    contacts = CustomerContact.objects.filter(customer=customer)

    # ✅ Fetch only visits for this customer
    new_visits = (
        NewVisit.objects.filter(company_name=customer)
        .select_related("added_by", "contact_person")
        .order_by("-created_at")  # latest first
    )

    return render(request, "company/customer_detail.html", {
        "customer": customer,
        "contacts": contacts,
        "visits": new_visits,   # changed to just visits
    })





