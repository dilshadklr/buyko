from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Cart, OrderPayment, Product, Order, Banner
from .forms import EditUserProfileForm, ProductForm, BannerForm


#  HOME PAGE

from django.db.models import Q

def index(request):
    query = request.GET.get("q", "").strip()

    all_products = Product.objects.all().order_by('-created_at')

    
    search_results = None
    if query:
        search_results = all_products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

  
    new_products = all_products[:9]

  
    banners = Banner.objects.all().order_by('-created_at')

    return render(request, 'buykoapp/index.html', {
        'products': all_products,
        'search_results': search_results,
        'new_products': new_products,
        'banners': banners,
        'query': query,
    })




# ADMIN DASHBOARD

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product
from .forms import ProductForm

def admin_dashboard(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Product added successfully!")
        return redirect('admin_dashboard')

    products = Product.objects.all().order_by('-created_at')

 
    total_products = products.count()
    total_stock = sum([p.quantity for p in products])
    low_stock_count = products.filter(quantity__lte=5).count()
    out_of_stock_count = products.filter(quantity=0).count()

    return render(request, 'buykoapp/adminhome.html', {
        'form': form,
        'products': products,
        'total_products': total_products,
        'total_stock': total_stock,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count
    })


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully!")
        return redirect('admin_dashboard')

    return render(request, 'buykoapp/edit_product.html', {
        'form': form,
        'product': product
    })


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))





from django.shortcuts import render
from .models import Product

def admin_stock(request):
    products = Product.objects.all().order_by('category')

    total_stock = sum([p.quantity for p in products])
    low_stock_count = products.filter(quantity__lte=5).count()
    out_of_stock_count = products.filter(quantity=0).count()

    return render(request, 'buykoapp/admin_stock.html', {
        'products': products,
        'total_stock': total_stock,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count
    })




# CATEGORY PAGE

def category_page(request, category_name):
    products = Product.objects.filter(
        category__iexact=category_name
    ).order_by('-created_at')

    return render(request, 'buykoapp/category.html', {
        'category_name': category_name,
        'products': products
    })



#  CART SYSTEM 

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Cart

@login_required(login_url='login_user')
def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, "Quantity updated in cart.")
    else:
        messages.success(request, "Product added to cart.")

    return redirect(request.META.get("HTTP_REFERER", "index"))






@login_required(login_url='login_user')
def cart(request):

    cart_items = Cart.objects.filter(user=request.user)


    total = sum(item.total_price for item in cart_items)

    return render(request, 'buykoapp/cart.html', {
        "cart_items": cart_items,
        "total": total
    })



@login_required(login_url='login_user')
def remove_cart(request, product_id):
    
    item = Cart.objects.filter(user=request.user, product_id=product_id).first()

    if item:
        item.delete()
        messages.success(request, "Item removed from cart.")

    return redirect("cart")





def increase_quantity(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)

    if item_id in cart:
        cart[item_id] += 1

    request.session['cart'] = cart
    return redirect('cart')


def decrease_quantity(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)

    if item_id in cart:
        cart[item_id] -= 1
        if cart[item_id] <= 0:
            del cart[item_id]

    request.session['cart'] = cart
    return redirect('cart')



# CART SUCCESS

def cartsuccess(request):
    return render(request, 'buykoapp/cartsuccess.html')


#  PAYMENT & ORDER


def cod_payment(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        name = request.POST.get("full_name")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        pincode = request.POST.get("pincode")
        state = request.POST.get("state")
        city = request.POST.get("city")
        quantity = int(request.POST.get("quantity"))
        total_price = product.price * quantity

        Order.objects.create(
            product=product,
            quantity=quantity,
            full_name=name,
            mobile=mobile,
            address=address,
            pincode=pincode,
            state=state,
            city=city,
            total_price=total_price,
            payment_method="COD",
            status="Order Placed"
        )

        messages.success(request, "Order placed successfully!")
        return redirect("order_success")

    return render(request, "buykoapp/cod_payment.html", {"product": product})


def cart_checkout(request):
    cart_data = request.session.get('cart', {})
    if not cart_data:
        messages.error(request, "Your cart is empty!")
        return redirect('cart')

    cart_items = []
    total = 0

    for pid, qty in cart_data.items():
        product = get_object_or_404(Product, id=pid)
        total_price = product.price * qty
        total += total_price

        cart_items.append({
            'product': product,
            'quantity': qty,
            'total_price': total_price
        })

    if request.method == "POST":
        name = request.POST.get("name")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")

        for item in cart_items:
            Order.objects.create(
                product=item['product'],
                quantity=item['quantity'],
                total_price=item['total_price'],
                full_name=name,
                mobile=mobile,
                address=address,
                city=city,
                state=state,
                pincode=pincode,
                payment_method="COD",
                status="Order Placed"
            )

        request.session['cart'] = {}
        messages.success(request, "Your order has been placed successfully!")
        return redirect("order_success")

    return render(request, "buykoapp/cart_checkout.html", {
        "cart_items": cart_items,
        "total": total
    })


def order_success(request):
    return render(request, "buykoapp/order_success.html")


#  BANNERS


def add_banner(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_banner')
    else:
        form = BannerForm()

    banners = Banner.objects.all().order_by('-id')

    return render(request, 'buykoapp/add_banner.html', {
        'form': form,
        'banners': banners,
    })


def delete_banner(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    banner.delete()
    return redirect('add_banner')



# ADMIN HOME


def adminhome(request):
    return render(request, 'buykoapp/adminhome.html')





from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm
from .models import UserProfile

def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data.get("name")
            email = form.cleaned_data.get("email")
            mobile = form.cleaned_data.get("mobile")
            gender = form.cleaned_data.get("gender")
            address = form.cleaned_data.get("address")
            password = form.cleaned_data.get("password")


            parts = name.split()
            first_name = parts[0]
            last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

           
            user = User(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            user.set_password(password)
            user.save()

        
            UserProfile.objects.create(
                user=user,
                mobile=mobile,
                gender=gender,
                address=address
            )

            messages.success(request, "Account created successfully!")
            return redirect("login_user")

    else:
        form = RegisterForm()

    return render(request, "buykoapp/register.html", {"form": form})



def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

     
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "Email not found!")
            return redirect("login_user")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("index")
        else:
            messages.error(request, "Incorrect password!")
            return redirect("login_user")

    return render(request, "buykoapp/login.html")


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("index")




from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Cart

@login_required(login_url='login_user')
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum([item.total_price() for item in cart_items])

    return render(request, 'buykoapp/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })




import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product, Cart, Order, OrderItem

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))



# RAZORPAY CHECKOUT FOR CART


@login_required(login_url='login_user')
def razorpay_cart_payment(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart")


    total_amount = sum(item.total_price for item in cart_items)
    amount_paise = int(total_amount * 100)

    razorpay_order = razorpay_client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"order_rcpt_{request.user.id}",
        "payment_capture": 1,
    })

    # Save order

    order = Order.objects.create(
        user=request.user,
        total_amount=total_amount,
        order_id=razorpay_order["id"],
        paid=False
    )

    context = {
        "cart_items": cart_items,
        "total_amount": total_amount,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount_paise": amount_paise,
        "callback_url": request.build_absolute_uri('/razorpay/verify/')
    }

    return render(request, "buykoapp/razorpay_cart_checkout.html", context)


# VERIFY PAYMENT


@csrf_exempt
def razorpay_verify(request):
    if request.method != "POST":
        return redirect("index")

    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    try:
        order = Order.objects.get(order_id=razorpay_order_id)
    except Order.DoesNotExist:
        return render(request, "buykoapp/payment_failed.html", {"msg": "Order not found."})

    params = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }

    try:
        razorpay_client.utility.verify_payment_signature(params)
    except:
        order.paid = False
        order.save()
        return render(request, "buykoapp/payment_failed.html", {"msg": "Payment verification failed."})

    # SUCCESS
    order.paid = True
    order.payment_id = razorpay_payment_id
    order.signature = razorpay_signature
    order.save()

    # Move cart items to order items
    cart_items = Cart.objects.filter(user=order.user)
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
    cart_items.delete()

    return render(request, "buykoapp/payment_success.html", {"order": order})



# SINGLE PRODUCT PAYMENT


@login_required(login_url='login_user')
def razorpay_create_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    amount_paise = int(product.price * 100)

    razorpay_order = razorpay_client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"single_order_{product_id}_{request.user.id}",
        "payment_capture": 1,
    })

    # Save in OrderPayment, not Order
    order_payment = OrderPayment.objects.create(
        user=request.user,
        product=product,
        amount=product.price,
        total_amount=product.price,
        razorpay_order_id=razorpay_order["id"],
        paid=False
    )

    context = {
        "product": product,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount_paise": amount_paise,
        "callback_url": request.build_absolute_uri('/razorpay/verify_single/')
    }

    return render(request, "buykoapp/razorpay_checkout.html", context)






@csrf_exempt
@login_required
def razorpay_verify_single(request):
    if request.method != "POST":
        return redirect("index")

    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    try:
        payment = OrderPayment.objects.get(razorpay_order_id=razorpay_order_id)
    except OrderPayment.DoesNotExist:
        return render(request, "buykoapp/payment_failed.html", {"msg": "Order not found."})

    params = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }

    try:
        razorpay_client.utility.verify_payment_signature(params)
    except:
        payment.paid = False
        payment.save()
        return render(request, "buykoapp/payment_failed.html", {"msg": "Payment verification failed."})

    payment.paid = True
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.save()

    return render(request, "buykoapp/payment_success.html", {"order": payment})






# ADMIN ALL ORDERS


from django.shortcuts import render
from .models import Order, OrderPayment

def admin_orders(request):
    # Cart orders
    orders = Order.objects.all().order_by('-id')

    # Single product orders
    single_orders = OrderPayment.objects.filter(product__isnull=False).order_by('-id')

    context = {
        "orders": orders,
        "single_orders": single_orders
    }
    return render(request, "buykoapp/admin_orders.html", context)




# USER ORDER PAGE


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, "buykoapp/order.html", {"orders": orders})





from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EditProfileForm, EditUserProfileForm
from django.contrib.auth.models import User
from .models import UserProfile




@login_required(login_url='login_user')
def user_details(request):
    user = User.objects.get(pk=request.user.pk) 
    return render(request, "buykoapp/user_details.html", {"user": user})


@login_required(login_url='login_user')
def edit_profile(request):
    user = request.user

    # FIX: create profile if missing
    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=user)
        profile_form = EditUserProfileForm(request.POST, instance=profile)

        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('user_details')
    else:
        form = EditProfileForm(instance=user)
        profile_form = EditUserProfileForm(instance=profile)

    return render(request, "buykoapp/edit_profile.html", {
        "form": form,
        "profile_form": profile_form,
    })







from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from .models import PasswordResetOTP
from .forms import OTPForm, VerifyOTPForm, ResetPasswordForm
import random


# STEP 1 - SEND OTP
def password_reset_request(request):
    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Email not found.")
                return redirect("password_reset_request")

            otp_code = str(random.randint(100000, 999999))
            PasswordResetOTP.objects.create(user=user, otp=otp_code)

            send_mail(
                "Your Buyko Password Reset OTP",
                f"Your OTP is: {otp_code}. Valid for 10 minutes.",
                None,
                [email],
            )

            request.session["reset_email"] = email
            messages.success(request, f"OTP sent to {email}")
            return redirect("password_reset_verify")
    else:
        form = OTPForm()

    return render(request, "buykoapp/password_reset_request.html", {"form": form})


# STEP 2 - VERIFY OTP
def password_reset_verify(request):
    email = request.session.get("reset_email")

    if not email:
        messages.error(request, "Session expired. Start again.")
        return redirect("password_reset_request")

    user = User.objects.get(email=email)

    if request.method == "POST":
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data["otp"]

            otp_obj = PasswordResetOTP.objects.filter(
                user=user, otp=otp, is_used=False
            ).last()

            if otp_obj and otp_obj.is_valid():
                request.session["reset_otp"] = otp
                return redirect("password_reset_confirm")

            messages.error(request, "Invalid or expired OTP.")
    else:
        form = VerifyOTPForm()

    return render(request, "buykoapp/password_reset_verify.html", {"form": form})


# STEP 3 - SET NEW PASSWORD
def password_reset_confirm(request):
    email = request.session.get("reset_email")
    otp = request.session.get("reset_otp")

    if not email or not otp:
        messages.error(request, "Session expired. Start again.")
        return redirect("password_reset_request")

    user = User.objects.get(email=email)

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_pw = form.cleaned_data["new_password"]

            user.set_password(new_pw)
            user.save()

            otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).last()
            otp_obj.is_used = True
            otp_obj.save()

            del request.session["reset_email"]
            del request.session["reset_otp"]

            messages.success(request, "Password successfully reset.")
            return redirect("login_user")
    else:
        form = ResetPasswordForm(initial={"email": email, "otp": otp})

    return render(request, "buykoapp/password_reset_new.html", {"form": form})








from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone

def admin_users(request):

    # Get all active sessions
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    active_user_ids = []

    for session in sessions:
        data = session.get_decoded()
        if "_auth_user_id" in data:
            active_user_ids.append(int(data["_auth_user_id"]))

    # Get all registered users
    users = User.objects.all()

    # Attach active status
    for u in users:
        u.is_active_session = u.id in active_user_ids

    return render(request, "buykoapp/users.html", {"users": users})




from django.contrib.auth.models import User
from django.shortcuts import redirect

def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('admin_users')















# buykoapp/views.py (add these imports at top)
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Sum, F, FloatField, ExpressionWrapper, Count
from datetime import datetime, timedelta
from io import BytesIO

# models
from .models import Product, Order, OrderItem

# reportlab for PDF
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def sales_report(request):
    end_date = request.GET.get('end')
    start_date = request.GET.get('start')

    # Parse end date
    try:
        if end_date:
            end = timezone.make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
            end = timezone.make_aware(datetime.combine(end.date(), datetime.max.time()))
        else:
            end = timezone.now()
    except Exception:
        end = timezone.now()

    # Parse start date
    try:
        if start_date:
            start = timezone.make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
            start = timezone.make_aware(datetime.combine(start.date(), datetime.min.time()))
        else:
            start = end - timedelta(days=30)
    except Exception:
        start = end - timedelta(days=30)

    # Paid orders only
    orders_qs = Order.objects.filter(paid=True, created_at__range=(start, end))

    total_orders = orders_qs.count()
    total_income = orders_qs.aggregate(total=Sum('total_amount'))['total'] or 0

    items_in_range = OrderItem.objects.filter(order__in=orders_qs)
    total_qty = items_in_range.aggregate(total=Sum('quantity'))['total'] or 0

    sold_products = (
        items_in_range
        .values('product__name')
        .annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum(
                ExpressionWrapper(
                    F('quantity') * F('price'),
                    output_field=FloatField()
                )
            )
        )
        .order_by('-quantity_sold')
    )

    # Table + Graph data
    top_products = []
    product_labels = []
    product_qty = []
    product_revenue = []

    for p in sold_products:
        name = p['product__name'] or "Unknown"
        qty = int(p['quantity_sold'] or 0)
        revenue = float(p['revenue'] or 0)

        top_products.append({
            'name': name,
            'quantity_sold': qty,
            'revenue': revenue,
        })

        product_labels.append(name)
        product_qty.append(qty)
        product_revenue.append(revenue)

    context = {
        'start': start.date(),
        'end': end.date(),
        'total_orders': total_orders,
        'total_income': float(total_income),
        'total_qty': int(total_qty),
        'top_products': top_products,
        'orders_qs': orders_qs,

        # Graph data
        'product_labels': product_labels,
        'product_qty': product_qty,
        'product_revenue': product_revenue,
    }

    return render(request, 'buykoapp/sales_report.html', context)





def sales_report_pdf(request):
    """
    Generate PDF for the same date range and data.
    Accepts GET params same as sales_report: start, end
    """
    # reuse date parsing logic
    end_date = request.GET.get('end')
    start_date = request.GET.get('start')

    try:
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end = timezone.now()
        end = timezone.make_aware(datetime.combine(end.date(), datetime.max.time()))
    except Exception:
        end = timezone.now()

    try:
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start = end - timedelta(days=30)
        start = timezone.make_aware(datetime.combine(start.date(), datetime.min.time()))
    except Exception:
        start = end - timedelta(days=30)

    orders_qs = Order.objects.filter(paid=True, created_at__range=(start, end))
    items_in_range = OrderItem.objects.filter(order__in=orders_qs)

    total_orders = orders_qs.count()
    total_income = orders_qs.aggregate(total=Sum('total_amount'))['total'] or 0
    total_qty = items_in_range.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    sold_products = (
        items_in_range
        .values('product__name')
        .annotate(quantity_sold=Sum('quantity'),
                  revenue=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=FloatField())))
        .order_by('-quantity_sold')
    )

    # Build PDF
    buffer = BytesIO()
    # Landscape A4 if many columns, else A4 portrait. Use A4 portrait
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)

    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph(f"Buyko — Sales Report ({start.date()} — {end.date()})", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Summary
    summary_data = [
        ['Total Orders', str(total_orders)],
        ['Total Quantity Sold', str(int(total_qty))],
        ['Total Income (₹)', f"₹{float(total_income):,.2f}"],
    ]
    t = Table(summary_data, colWidths=[200, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 16))

    # Top products table
    prod_table_data = [['#', 'Product', 'Qty Sold', 'Revenue (₹)']]
    i = 1
    for p in sold_products:
        prod_table_data.append([
            str(i),
            p.get('product__name') or 'Unknown',
            str(int(p.get('quantity_sold') or 0)),
            f"₹{float(p.get('revenue') or 0.0):,.2f}"
        ])
        i += 1

    prod_table = Table(prod_table_data, colWidths=[30, 260, 80, 100])
    prod_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#001f4d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    elements.append(Paragraph("Top Sold Products", styles['Heading2']))
    elements.append(Spacer(1, 8))
    elements.append(prod_table)

    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    filename = f"sales_report_{start.date()}_to_{end.date()}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    return response








