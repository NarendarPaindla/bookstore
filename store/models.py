from django.db import models
from django.urls import reverse
from django.utils.text import slugify

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
