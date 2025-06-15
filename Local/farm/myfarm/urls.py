from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from farm import views


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # Static pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('how-it-works/', views.HowItWorksView.as_view(), name='how_it_works'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),

    # Products
    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Farmers
    path('farmers/', views.FarmerListView.as_view(), name='farmers'),
    path('farmers/<int:pk>/', views.FarmerDetailView.as_view(), name='farmer_detail'),

    # Cart and checkout
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation_view, name='order_confirmation'),
]