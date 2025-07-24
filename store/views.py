from django.shortcuts             import render, redirect
from django.contrib.auth          import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms                       import SignupForm
from django.contrib.auth.forms    import AuthenticationForm
from django.core.paginator import Paginator
from .models import Book, Category, Publisher
def home(request):
    return render(request, 'base.html')

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