from django.contrib import admin
from .models import Category, Publisher, Language, Book

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Language)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'stock', 'rating')
    list_filter  = ('category', 'publisher', 'language', 'book_format')
    prepopulated_fields = {'slug': ('title',)}
