from django.shortcuts import render,redirect,get_object_or_404

# Create your views here.
from .models import Product,Registration
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.hashers import make_password,check_password
import json



# user login
@csrf_exempt
def user_registration(request):
    if request.method =="POST":
        data=json.loads(request.body)
        email=data.get("email")

        if Registration.objects.filter(email=email).exists():
            return JsonResponse(
                {
                    "Error":"User Already Exists"
                }
            )
        Registration.objects.create(
            first_name=data.get("first_name"),
            middle_name=data.get("middle_name"),
            last_name=data.get("last_name"),
            email=email,
            password=make_password(data.get("password")),

        )

        return JsonResponse(
            {
                "Message":"User Registered Successfully"
            }
        )
    else:
        return JsonResponse(
            {
                "Error":"choose correct method"
            }
        )



# Default login: username rutikdughad, password Rutik@2110
_DEFAULT_LOGIN_EMAIL = "rutikdughad@productcatalog.com"
_DEFAULT_LOGIN_PASSWORD = "Rutik@2110"


def _ensure_default_user():
    """Create or update default user (rutikdughad / Rutik@2110)."""
    user, created = Registration.objects.get_or_create(
        email=_DEFAULT_LOGIN_EMAIL,
        defaults={
            'first_name': 'Rutik',
            'middle_name': '',
            'last_name': 'Dughad',
            'password': make_password(_DEFAULT_LOGIN_PASSWORD),
        }
    )
    # If user exists, update password to ensure it's correct
    if not created:
        user.password = make_password(_DEFAULT_LOGIN_PASSWORD)
        user.first_name = 'Rutik'
        user.last_name = 'Dughad'
        user.save()


@csrf_exempt
def user_login(request):
    if request.method == "POST":
        _ensure_default_user()
        data = json.loads(request.body)
        email_or_username = (data.get("email") or "").strip()
        password = data.get("password") or ""

        # If user enters "rutikdughad" (no @), treat as username and append @productcatalog.com
        if email_or_username and "@" not in email_or_username:
            email_or_username = email_or_username + "@productcatalog.com"

        try:
            queryset = Registration.objects.get(email=email_or_username)

            if check_password(password, queryset.password):
                # Set session for logged in user
                request.session['user_id'] = queryset.id
                request.session['user_name'] = queryset.first_name
                request.session['user_email'] = queryset.email
                request.session.set_expiry(86400)  # 24 hours
                
                return JsonResponse(
                    {
                        "Message": "Login Succesfully",
                        "user id": queryset.id,
                        "user name": queryset.first_name
                    }
                )
            else:
                return JsonResponse(
                    {"Error": "Invalid Password"}
                )
        except Registration.DoesNotExist:
            return JsonResponse(
                {"Error": "User Not Found"}
            )
    else:
        return JsonResponse(
            {"Error": "choose correct method"}
        )


def user_logout(request):
    """Logout user and clear session."""
    request.session.flush()
    return redirect('Products_app:home')
    




# def product_list(request):
#     if request.method == 'GET':

#         products = Product.objects.all()
#         return JsonResponse(
#              {
#                 'products': list(products.values())        
#       })



# Home page
def home(request):
    # If logged in, redirect to manage products
    if 'user_id' in request.session:
        return redirect('Products_app:manage_products')
    return render(request, 'PCA_App/home.html')

# About page
def about(request):
    return render(request, 'PCA_App/about.html')

# Contact page
def contact(request):
    return render(request, 'PCA_App/contact.html')

# Login page (template-based)
def login_page(request):
    return render(request, 'PCA_App/login.html')

# ascess the product list 
def product_list(request):
    if request.method == 'GET':
        from urllib.parse import unquote
        category = request.GET.get('category', 'all')
        
        # Decode URL-encoded category names (handles "Home & Living" with &)
        if category != 'all' and category:
            category = unquote(category)
        
        if category == 'all' or category == '':
            products = Product.objects.all()
        else:
            # Use exact match for category filtering
            products = Product.objects.filter(category=category)
        
        # Get all unique categories for the filter dropdown
        all_categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')
        
        return render(request, 'PCA_App/product_list.html', {
            'products': products,
            'selected_category': category,
            'all_categories': all_categories
        })

# add product

@csrf_exempt
def add_product(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        product = Product.objects.create(
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price'),
            category=data.get('category'),
            is_available=data.get('is_available', True)
        )

        return JsonResponse({
            "message": "Product added successfully",
            "id": product.id
        })





# Update product
@csrf_exempt
def product_update(request, id):
    if request.method == 'PUT':
        product = get_object_or_404(Product, id=id)
        data = json.loads(request.body)

        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.category = data.get('category', product.category)
        product.is_available = data.get('is_available', product.is_available)

        product.save()

        return JsonResponse({
            "message": "Product updated successfully",
            "product_id": product.id
        }, status=200)

    return JsonResponse({
        "error": "Only PUT method allowed"
    }, status=405)




# Delete product
@csrf_exempt
def product_delete(request, id):
    if request.method == 'DELETE':
        product = get_object_or_404(Product, id=id)
        product.delete()

        return JsonResponse({
            "status": "success",
            "message": "Product deleted successfully"
        })

    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    }, status=405)


# --- Admin: Manage Products (Add/Update/Delete) ---

def manage_products(request):
    """Admin: List all products with Edit/Delete actions."""
    products = Product.objects.all().order_by('-updated_at')
    return render(request, 'PCA_App/manage_products.html', {'products': products})


def add_product_page(request):
    """Admin: Form to add a new product."""
    redirect_to = request.GET.get('next', 'product_list')  # Default to product_list
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '0')
        category = request.POST.get('category', '').strip()
        is_available = request.POST.get('is_available') == 'on'
        redirect_after = request.POST.get('next', redirect_to)
        
        if name and category:
            try:
                p = float(price) if price else 0
                if p < 0:
                    p = 0
                Product.objects.create(
                    name=name,
                    description=description,
                    price=p,
                    category=category,
                    is_available=is_available
                )
                # Redirect to product_list if coming from there, else manage_products
                if redirect_after == 'product_list':
                    return redirect('Products_app:product_list')
                else:
                    return redirect('Products_app:manage_products')
            except (ValueError, TypeError):
                pass
        return render(request, 'PCA_App/add_product.html', {
            'error': 'Please fill Name and Category. Price must be a valid number.',
            'name': name, 'description': description, 'price': price, 'category': category, 'is_available': is_available,
            'next': redirect_after
        })
    return render(request, 'PCA_App/add_product.html', {'next': redirect_to})


def edit_product_page(request, id):
    """Admin: Form to edit an existing product."""
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name).strip()
        product.description = request.POST.get('description', product.description).strip()
        product.category = request.POST.get('category', product.category).strip()
        try:
            p = request.POST.get('price') or 0
            product.price = max(0, float(p))
        except (ValueError, TypeError):
            pass
        product.is_available = request.POST.get('is_available') == 'on'
        if product.name and product.category:
            product.save()
            return redirect('Products_app:manage_products')
        return render(request, 'PCA_App/edit_product.html', {
            'product': product,
            'error': 'Name and Category are required. Price must be a valid number.'
        })
    return render(request, 'PCA_App/edit_product.html', {'product': product})


def delete_product_confirm(request, id):
    """Admin: Confirm and delete a product."""
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.delete()
        return redirect('Products_app:manage_products')
    return render(request, 'PCA_App/delete_product_confirm.html', {'product': product})


def create_sample_products(request):
    """Create 40 sample products: 10 Electronics, 10 Fashion, 10 Home & Living, 10 Gifts."""
    categories_data = {
        'Electronics': [
            {'name': 'Smartphone Pro Max', 'description': 'Latest smartphone with advanced camera and 5G connectivity', 'price': 899.99},
            {'name': 'Wireless Headphones', 'description': 'Premium noise-cancelling wireless headphones', 'price': 249.99},
            {'name': 'Laptop Ultra', 'description': 'High-performance laptop for work and gaming', 'price': 1299.99},
            {'name': 'Smart Watch', 'description': 'Fitness tracking smartwatch with health monitoring', 'price': 299.99},
            {'name': 'Tablet 10-inch', 'description': 'Versatile tablet perfect for entertainment and productivity', 'price': 449.99},
            {'name': 'Bluetooth Speaker', 'description': 'Portable speaker with 360-degree sound', 'price': 79.99},
            {'name': 'Gaming Mouse', 'description': 'Precision gaming mouse with RGB lighting', 'price': 59.99},
            {'name': 'Mechanical Keyboard', 'description': 'RGB mechanical keyboard with tactile switches', 'price': 129.99},
            {'name': '4K Monitor', 'description': '27-inch 4K UHD monitor for professional work', 'price': 399.99},
            {'name': 'Webcam HD', 'description': '1080p HD webcam with auto-focus and noise reduction', 'price': 89.99},
        ],
        'Fashion': [
            {'name': 'Designer T-Shirt', 'description': 'Premium cotton t-shirt with modern design', 'price': 39.99},
            {'name': 'Denim Jeans', 'description': 'Classic fit jeans with stretch comfort', 'price': 79.99},
            {'name': 'Leather Jacket', 'description': 'Genuine leather jacket with modern style', 'price': 199.99},
            {'name': 'Running Shoes', 'description': 'Comfortable running shoes with cushioned sole', 'price': 119.99},
            {'name': 'Sunglasses', 'description': 'UV protection sunglasses with polarized lenses', 'price': 49.99},
            {'name': 'Wristwatch', 'description': 'Elegant wristwatch with leather strap', 'price': 149.99},
            {'name': 'Backpack', 'description': 'Stylish backpack with laptop compartment', 'price': 69.99},
            {'name': 'Hoodie', 'description': 'Warm and comfortable hoodie for casual wear', 'price': 59.99},
            {'name': 'Dress Shirt', 'description': 'Formal dress shirt perfect for business occasions', 'price': 54.99},
            {'name': 'Sneakers', 'description': 'Trendy sneakers with breathable mesh upper', 'price': 89.99},
        ],
        'Home & Living': [
            {'name': 'Coffee Maker', 'description': 'Programmable coffee maker with thermal carafe', 'price': 89.99},
            {'name': 'Air Purifier', 'description': 'HEPA air purifier for clean indoor air', 'price': 199.99},
            {'name': 'Table Lamp', 'description': 'Modern LED table lamp with adjustable brightness', 'price': 49.99},
            {'name': 'Throw Pillow Set', 'description': 'Set of 4 decorative throw pillows', 'price': 39.99},
            {'name': 'Wall Clock', 'description': 'Elegant wall clock with silent movement', 'price': 34.99},
            {'name': 'Desk Organizer', 'description': 'Bamboo desk organizer for office supplies', 'price': 24.99},
            {'name': 'Plant Pot Set', 'description': 'Set of 3 ceramic plant pots with drainage', 'price': 29.99},
            {'name': 'Cushion Cover', 'description': 'Decorative cushion covers, set of 2', 'price': 19.99},
            {'name': 'Photo Frame', 'description': 'Wooden photo frame for 8x10 photos', 'price': 14.99},
            {'name': 'Candle Set', 'description': 'Scented candle set with 3 fragrances', 'price': 27.99},
        ],
        'Gifts': [
            {'name': 'Gift Basket', 'description': 'Premium gift basket with assorted treats', 'price': 49.99},
            {'name': 'Chocolate Box', 'description': 'Luxury chocolate box with 24 pieces', 'price': 34.99},
            {'name': 'Flower Bouquet', 'description': 'Fresh flower bouquet with elegant arrangement', 'price': 39.99},
            {'name': 'Wine Set', 'description': 'Premium wine set with 2 bottles', 'price': 79.99},
            {'name': 'Gift Card', 'description': 'Gift card worth $50 for any purchase', 'price': 50.00},
            {'name': 'Jewelry Box', 'description': 'Elegant jewelry box with velvet lining', 'price': 29.99},
            {'name': 'Perfume Set', 'description': 'Luxury perfume set with 3 fragrances', 'price': 59.99},
            {'name': 'Teddy Bear', 'description': 'Soft plush teddy bear, perfect gift', 'price': 24.99},
            {'name': 'Photo Album', 'description': 'Leather-bound photo album for memories', 'price': 19.99},
            {'name': 'Gift Wrap Set', 'description': 'Premium gift wrap set with ribbons', 'price': 14.99},
        ]
    }
    
    created_count = 0
    for category, products in categories_data.items():
        for product_data in products:
            if not Product.objects.filter(name=product_data['name'], category=category).exists():
                Product.objects.create(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    category=category,
                    is_available=True
                )
                created_count += 1
    
    return JsonResponse({
        'message': f'Sample products created successfully. {created_count} new products added.',
        'created': created_count
    })

