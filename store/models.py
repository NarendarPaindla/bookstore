from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Publisher(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    FORMAT_CHOICES = (
        ('ebook', 'E‑Book'),
        ('hardcopy', 'Hardcopy'),
    )
    title       = models.CharField(max_length=200)
    slug        = models.SlugField(blank=True, unique=True)
    author      = models.CharField(max_length=150)
    isbn        = models.CharField(max_length=13, unique=True)
    price       = models.DecimalField(max_digits=6, decimal_places=2)
    stock       = models.PositiveIntegerField(default=0)
    language    = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    book_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='hardcopy')
    description = models.TextField()
    preview     = models.FileField(upload_to='previews/', blank=True, null=True)
    cover_img   = models.ImageField(upload_to='covers/', blank=True, null=True)
    rating      = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    publisher   = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True)
    created     = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('book_detail', args=[self.slug])

    def __str__(self):
        return self.title
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('paid',      'Paid'),
        ('shipped',   'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    created     = models.DateTimeField(auto_now_add=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    full_name   = models.CharField(max_length=100)
    address     = models.CharField(max_length=255)
    city        = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country     = models.CharField(max_length=100)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    @property
    def total(self):
        return sum(item.price * item.quantity for item in self.items.all())

class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book     = models.ForeignKey('Book', on_delete=models.CASCADE)
    price    = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.book.title}"

class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book     = models.ForeignKey(Book, on_delete=models.CASCADE)
    price    = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.book.title}"
class Review(models.Model):
    RATING_CHOICES = [(i, f"{i} Star{'s' if i>1 else ''}") for i in range(1,6)]
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    book     = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='reviews')
    rating   = models.IntegerField(choices=RATING_CHOICES)
    text     = models.TextField()
    created  = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.rating}★ by {self.user.username} on {self.book.title}"