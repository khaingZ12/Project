from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import *
from .forms import *

# Create your views here.

# Static Pages
class HomeView(TemplateView):
    template_name = 'myfarm/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(available_quantity__gt=0)[:8]
        context['featured_farmers'] = FarmerProfile.objects.all()[:4]
        return context
        
class AboutView(TemplateView):
    template_name = 'myfarm/about.html'

class HowItWorksView(TemplateView):
    template_name = 'myfarm/how-it-works.html'

class ContactView(TemplateView):
    template_name = 'myfarm/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_success')
        return render(request, self.template_name, {'form': form})
    

class FAQView(ListView):
    model = FAQ
    template_name = 'myfarm/faq.html'
    context_object_name = 'faqs'

class TermsView(TemplateView):
    template_name = 'myfarm/terms.html'

class PrivacyView(TemplateView):
    template_name = 'myfarm/privacy.html'


# Authentication
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'myfarm/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'myfarm/signup.html', {'form': form})

# Products
class ProductListView(ListView):
    model = Product
    template_name = 'myfarm/products.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(available_quantity__gt=0)

# Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by farmer
        farmer_id = self.request.GET.get('farmer')
        if farmer_id:
            queryset = queryset.filter(farmer__id=farmer_id)
        
        # Filter by organic
        organic = self.request.GET.get('organic')
        if organic == 'true':
            queryset = queryset.filter(is_organic=True)

            # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(farmer__farm_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.all()
        context['farmers'] = FarmerProfile.objects.all()
        return context
    
class ProductDetailView(DetailView):
    model = Product
    template_name = 'myfarm/product_detail.html'
    context_object_name = 'product'


# Farmers
class FarmerListView(ListView):
    model = FarmerProfile
    template_name = 'myfarm/farmers.html'
    context_object_name = 'farmers'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(farm_name__icontains=search) | 
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        return queryset


class FarmerDetailView(DetailView):
    model = FarmerProfile
    template_name = 'myfarm/farmer_detail.html'
    context_object_name = 'farmer'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(farmer=self.object, available_quantity__gt=0)
        return context
    

# Cart and Checkout
@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'myfarm/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart')

@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = Order.objects.create(
                customer=request.user,
                total_amount=cart.total,
                delivery_address=form.cleaned_data['delivery_address'],
                delivery_date=form.cleaned_data['delivery_date'],
                notes=form.cleaned_data['notes']
            )

    # Create order items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                
                # Update product quantity
                item.product.available_quantity -= item.quantity
                item.product.save()

                # Clear cart
            cart.items.all().delete()
            
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm(initial={
            'delivery_address': request.user.address
        })
    
    return render(request, 'myfarm/checkout.html', {
        'cart': cart,
        'form': form
    })

@login_required
def order_confirmation_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'myfarm/order_confirmation.html', {'order': order})