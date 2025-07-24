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
]
