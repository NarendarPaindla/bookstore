from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user-dashboard/',  views.user_dashboard,  name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('books/',          views.book_list,   name='book_list'),
    path('books/<slug:slug>/', views.book_detail, name='book_detail'),
    path('cart/',            views.cart,            name='cart'),
    path('cart/add/<slug:slug>/',    views.add_to_cart,    name='add_to_cart'),
    path('cart/remove/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/',     views.update_cart,     name='update_cart'),
    path('checkout/',        views.checkout,        name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('invoice/<int:order_id>/',      views.invoice_pdf,   name='invoice_pdf'),
    path('orders/',                        views.order_history, name='order_history'),
    path('orders/<int:order_id>/',         views.order_detail,  name='order_detail'),
    path('orders/<int:order_id>/cancel/',  views.cancel_order,  name='cancel_order'),
    path('orders/<int:order_id>/reorder/', views.reorder,       name='reorder'),
    path('downloads/',               views.downloads,      name='downloads'),
    path('download/<int:item_pk>/',  views.download_book,  name='download_book'),
    path('books/<slug:slug>/reviews/',     views.review_list,   name='review_list'),
    path('books/<slug:slug>/reviews/new/', views.review_create, name='review_create'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
