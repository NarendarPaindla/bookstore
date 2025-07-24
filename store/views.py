from django.shortcuts             import render, redirect,get_object_or_404
from django.contrib.auth          import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms                       import SignupForm
from django.contrib.auth.forms    import AuthenticationForm
from django.core.paginator import Paginator
from .models import Book, Category, Publisher,Order, OrderItem
from decimal                 import Decimal
from django.urls             import reverse
from django.http            import HttpResponse
from reportlab.pdfgen       import canvas
from reportlab.lib.pagesizes import letter
def home(request):
    featured = Book.objects.order_by('-created')[:6]
    return render(request, 'home.html', {'featured': featured})

def signup_view(request):
    form = SignupForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('admin_dashboard' if user.is_staff else 'user_dashboard')
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('admin_dashboard' if user.is_staff else 'user_dashboard')
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def user_dashboard(request):
    return render(request, 'user_dashboard.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')
def book_list(request):
    qs = Book.objects.select_related('category','publisher')
    # Filters
    category = request.GET.get('category')
    if category:
        qs = qs.filter(category__slug=category)
    author = request.GET.get('author')
    if author:
        qs = qs.filter(author__icontains=author)
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min: qs = qs.filter(price__gte=price_min)
    if price_max: qs = qs.filter(price__lte=price_max)

    # Search
    query = request.GET.get('q')
    if query:
        qs = qs.filter(title__icontains=query) | qs.filter(author__icontains=query)

    # Pagination (9 per page)
    paginator = Paginator(qs.distinct(), 9)
    page = request.GET.get('page')
    books = paginator.get_page(page)

    context = {
        'books': books,
        'categories': Category.objects.all(),
        'publishers': Publisher.objects.all(),
    }
    return render(request, 'books.html', context)

def book_detail(request, slug):
    book = Book.objects.get(slug=slug)
    return render(request, 'book_detail.html', {'book': book})
def _get_cart(request):
    return request.session.setdefault('cart', {})

def add_to_cart(request, slug):
    cart = _get_cart(request)
    book = get_object_or_404(Book, slug=slug)
    qty  = int(request.POST.get('quantity', 1))
    cart[str(book.id)] = cart.get(str(book.id), 0) + qty
    request.session.modified = True
    return redirect('cart')

def remove_from_cart(request, slug):
    cart = _get_cart(request)
    book = get_object_or_404(Book, slug=slug)
    cart.pop(str(book.id), None)
    request.session.modified = True
    return redirect('cart')

def update_cart(request):
    cart = _get_cart(request)
    for key, val in request.POST.items():
        if key.startswith('qty_'):
            book_id = key.split('_',1)[1]
            cart[book_id] = int(val)
    request.session.modified = True
    return redirect('cart')

@login_required
def cart(request):
    cart = _get_cart(request)
    items = []
    total = Decimal('0.00')
    for book_id, qty in cart.items():
        book = get_object_or_404(Book, id=book_id)
        line_total = book.price * qty
        items.append({'book': book, 'quantity': qty, 'line_total': line_total})
        total += line_total
    return render(request, 'cart.html', {'items': items, 'total': total})

@login_required
def checkout(request):
    if request.method == 'POST':
        # Create Order
        order = Order.objects.create(
            user=request.user,
            full_name   = request.POST['full_name'],
            address     = request.POST['address'],
            city        = request.POST['city'],
            postal_code = request.POST['postal_code'],
            country     = request.POST['country'],
            status='paid'  # Fake payment
        )
        cart = _get_cart(request)
        for book_id, qty in cart.items():
            book = get_object_or_404(Book, id=book_id)
            OrderItem.objects.create(
                order=order, book=book, price=book.price, quantity=qty
            )
        # Clear cart
        request.session['cart'] = {}
        return redirect(reverse('order_success', args=[order.id]))
    return render(request, 'checkout.html')

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
    return redirect('order_detail', order_id=order.id)

@login_required
def reorder(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = _get_cart(request)
    for item in order.items.all():
        cart[str(item.book.id)] = cart.get(str(item.book.id), 0) + item.quantity
    request.session.modified = True
    return redirect('cart')

@login_required
def invoice_pdf(request, order_id):
    # Fetch order, ensure ownership
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Prepare HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    # Create PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, f"Invoice for Order #{order.id}")
    y -= 30

    # Order metadata
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Date: {order.created.strftime('%Y-%m-%d %H:%M')}")
    y -= 20
    p.drawString(50, y, f"Customer: {order.user.username}")
    y -= 20
    p.drawString(50, y, f"Name: {order.full_name}")
    y -= 20
    p.drawString(50, y, f"Address: {order.address}, {order.city}, {order.postal_code}, {order.country}")
    y -= 30

    # Items
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Items:")
    y -= 20
    p.setFont("Helvetica", 12)
    total = 0
    for item in order.items.all():
        line = f"{item.book.title[:30]}… {item.quantity} × ${item.price} = ${item.price * item.quantity}"
        p.drawString(60, y, line)
        y -= 15
        total += item.price * item.quantity
        # New page if running out of space
        if y < 50:
            p.showPage()
            y = height - 50

    # Total
    y -= 10
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total: ${total:.2f}")

    p.showPage()
    p.save()
    return response