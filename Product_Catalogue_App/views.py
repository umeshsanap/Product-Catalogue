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
                    "Error":"Student Already Exist"
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
                "Message":"Student Registered Succesfully"
            }
        )
    else:
        return JsonResponse(
            {
                "Error":"choose correct method"
            }
        )



# user login
@csrf_exempt
def user_login(request):
    if request.method =="POST":
        data=json.loads(request.body)
        email=data.get("email")
        password=data.get("password")

        try:
            queryset=Registration.objects.get(email=email)

            if check_password(password,queryset.password):
                return JsonResponse(
                    {
                        "Message":"Login Succesfully",
                        "user id":queryset.id,
                        "user name":queryset.first_name
                    }
                )
            else:
                return JsonResponse(
                    {
                        "Error":"Invalid Password"
                    }
                )
        except Registration.DoesNotExist:
            return JsonResponse(
                {
                    "Error":"User Not Found"
                }
            )
    else:
        return JsonResponse(
            {
                "Error":"choose correct method"
            }
        )
    




# def product_list(request):
#     if request.method == 'GET':

#         products = Product.objects.all()
#         return JsonResponse(
#              {
#                 'products': list(products.values())        
#       })



# ascess the product list 
@csrf_exempt
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()

        return JsonResponse(
            {
                "status": "success",
                "count": products.count(),
                "products": list(products.values())
            },
            
        )

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

