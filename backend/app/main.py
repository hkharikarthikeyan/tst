from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from .models import UserCreate, UserLogin, Product, Subscription, Token, UserSubscription, CartItem, Order
from typing import Optional

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase setup
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/signup")
async def signup(user: UserCreate):
    # Check if user exists
    existing_user = supabase.table("users").select("*").eq("email", user.email).execute()
    if existing_user.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and create user
    hashed_password = pwd_context.hash(user.password)
    result = supabase.table("users").insert({
        "email": user.email,
        "password": hashed_password
    }).execute()
    
    if result.data:
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(status_code=400, detail="Registration failed")

@app.post("/login")
async def login(user: UserLogin):
    # Get user from database
    db_user = supabase.table("users").select("*").eq("email", user.email).execute()
    
    if not db_user.data or not pwd_context.verify(user.password, db_user.data[0]["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/products")
async def get_products():
    result = supabase.table("products").select("*").execute()
    return result.data

@app.post("/products")
async def create_product(product: Product, token: str = Depends(verify_token)):
    result = supabase.table("products").insert({
        "name": product.name,
        "price": product.price,
        "description": product.description
    }).execute()
    
    if result.data:
        return result.data[0]
    raise HTTPException(status_code=400, detail="Failed to create product")

@app.delete("/products/{product_id}")
async def delete_product(product_id: int, token: str = Depends(verify_token)):
    result = supabase.table("products").delete().eq("id", product_id).execute()
    return {"message": "Product deleted"}

@app.get("/subscriptions")
async def get_subscriptions():
    result = supabase.table("subscriptions").select("*").execute()
    return result.data

@app.post("/subscriptions")
async def create_subscription(subscription: Subscription, token: str = Depends(verify_token)):
    result = supabase.table("subscriptions").insert({
        "name": subscription.name,
        "price": subscription.price,
        "duration": subscription.duration,
        "features": subscription.features
    }).execute()
    
    if result.data:
        return result.data[0]
    raise HTTPException(status_code=400, detail="Failed to create subscription")

@app.delete("/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: int, token: str = Depends(verify_token)):
    result = supabase.table("subscriptions").delete().eq("id", subscription_id).execute()
    return {"message": "Subscription deleted"}

# User endpoints
@app.post("/user/signup")
async def user_signup(user: UserCreate):
    # Check if user exists
    existing_user = supabase.table("customers").select("*").eq("email", user.email).execute()
    if existing_user.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and create user
    hashed_password = pwd_context.hash(user.password)
    result = supabase.table("customers").insert({
        "email": user.email,
        "password": hashed_password,
        "name": user.name
    }).execute()
    
    if result.data:
        access_token = create_access_token(data={"sub": user.email, "type": "customer"})
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(status_code=400, detail="Registration failed")

@app.post("/user/login")
async def user_login(user: UserLogin):
    # Get user from database
    db_user = supabase.table("customers").select("*").eq("email", user.email).execute()
    
    if not db_user.data or not pwd_context.verify(user.password, db_user.data[0]["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email, "type": "customer"})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/user/products")
async def get_user_products():
    result = supabase.table("products").select("*").execute()
    return result.data

@app.get("/user/subscriptions")
async def get_user_subscriptions():
    result = supabase.table("subscriptions").select("*").execute()
    return result.data

@app.get("/user/profile")
async def get_user_profile(email: str = Depends(verify_token)):
    # Debug endpoint to check user info
    customer = supabase.table("customers").select("*").eq("email", email).execute()
    return {"email": email, "customer_found": bool(customer.data), "customer_data": customer.data}

@app.get("/debug/customers")
async def get_all_customers():
    # Debug endpoint to see all customers
    result = supabase.table("customers").select("*").execute()
    return result.data

@app.get("/test")
async def test_endpoint():
    return {"message": "Server is running with latest code", "timestamp": datetime.utcnow()}

@app.get("/debug/tables")
async def check_tables():
    try:
        # Check if tables exist by trying to query them
        customers = supabase.table("customers").select("count", count="exact").execute()
        products = supabase.table("products").select("count", count="exact").execute()
        subscriptions = supabase.table("subscriptions").select("count", count="exact").execute()
        
        try:
            customer_subs = supabase.table("customer_subscriptions").select("count", count="exact").execute()
            customer_subs_exists = True
        except:
            customer_subs_exists = False
            
        try:
            cart_items = supabase.table("cart_items").select("count", count="exact").execute()
            cart_items_exists = True
        except:
            cart_items_exists = False
            
        return {
            "customers": customers.count,
            "products": products.count,
            "subscriptions": subscriptions.count,
            "customer_subscriptions_exists": customer_subs_exists,
            "cart_items_exists": cart_items_exists
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/user/cart/add")
async def add_to_cart(item: CartItem, email: str = Depends(verify_token)):
    try:
        # Get customer ID
        customer = supabase.table("customers").select("id").eq("email", email).execute()
        if not customer.data:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        customer_id = customer.data[0]["id"]
        
        # Check if item already in cart
        existing = supabase.table("cart_items").select("*").eq("customer_id", customer_id).eq("product_id", item.product_id).execute()
        
        if existing.data:
            # Update quantity
            new_quantity = existing.data[0]["quantity"] + item.quantity
            result = supabase.table("cart_items").update({
                "quantity": new_quantity
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            # Add new item
            result = supabase.table("cart_items").insert({
                "customer_id": customer_id,
                "product_id": item.product_id,
                "quantity": item.quantity
            }).execute()
        
        return {"message": "Item added to cart"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/user/subscribe")
async def subscribe_to_plan(subscription: UserSubscription, email: str = Depends(verify_token)):
    try:
        print(f"Subscribe request - Email: {email}, Subscription ID: {subscription.subscription_id}")
        
        # Get customer ID
        customer = supabase.table("customers").select("id").eq("email", email).execute()
        print(f"Customer query result: {customer.data}")
        
        if not customer.data:
            raise HTTPException(status_code=404, detail=f"Customer not found for email: {email}")
        
        customer_id = customer.data[0]["id"]
        print(f"Customer ID: {customer_id}")
        
        # Check if subscription exists
        sub_check = supabase.table("subscriptions").select("id").eq("id", subscription.subscription_id).execute()
        print(f"Subscription check: {sub_check.data}")
        
        if not sub_check.data:
            raise HTTPException(status_code=404, detail="Subscription plan not found")
        
        # Check if already subscribed
        existing = supabase.table("customer_subscriptions").select("*").eq("customer_id", customer_id).eq("subscription_id", subscription.subscription_id).execute()
        print(f"Existing subscription check: {existing.data}")
        
        if existing.data:
            raise HTTPException(status_code=400, detail="Already subscribed to this plan")
        
        # Create subscription
        result = supabase.table("customer_subscriptions").insert({
            "customer_id": customer_id,
            "subscription_id": subscription.subscription_id,
            "status": "active"
        }).execute()
        
        print(f"Insert result: {result.data}")
        
        if result.data:
            return {"message": "Subscribed successfully", "subscription": result.data[0]}
        raise HTTPException(status_code=400, detail="Subscription failed")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Subscribe error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/user/my-subscriptions")
async def get_my_subscriptions(email: str = Depends(verify_token)):
    try:
        # Get customer ID
        customer = supabase.table("customers").select("id").eq("email", email).execute()
        if not customer.data:
            raise HTTPException(status_code=404, detail=f"Customer not found for email: {email}")
        
        customer_id = customer.data[0]["id"]
        
        # Get subscriptions with details
        result = supabase.table("customer_subscriptions").select(
            "*, subscriptions(name, price, duration, features)"
        ).eq("customer_id", customer_id).execute()
        
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



@app.get("/user/cart")
async def get_cart(email: str = Depends(verify_token)):
    # Get customer ID
    customer = supabase.table("customers").select("id").eq("email", email).execute()
    if not customer.data:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_id = customer.data[0]["id"]
    
    # Get cart items with product details
    result = supabase.table("cart_items").select(
        "*, products(name, price, description)"
    ).eq("customer_id", customer_id).execute()
    
    return result.data

@app.delete("/user/cart/{item_id}")
async def remove_from_cart(item_id: int, email: str = Depends(verify_token)):
    # Get customer ID
    customer = supabase.table("customers").select("id").eq("email", email).execute()
    if not customer.data:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_id = customer.data[0]["id"]
    
    # Remove item
    result = supabase.table("cart_items").delete().eq("id", item_id).eq("customer_id", customer_id).execute()
    return {"message": "Item removed from cart"}

@app.post("/user/orders")
async def create_order(order: Order, email: str = Depends(verify_token)):
    # Get customer ID
    customer = supabase.table("customers").select("id").eq("email", email).execute()
    if not customer.data:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_id = customer.data[0]["id"]
    
    # Create order
    order_result = supabase.table("orders").insert({
        "customer_id": customer_id,
        "total_amount": order.total_amount,
        "status": "pending"
    }).execute()
    
    if order_result.data:
        order_id = order_result.data[0]["id"]
        
        # Add order items
        for item in order.items:
            supabase.table("order_items").insert({
                "order_id": order_id,
                "product_id": item.product_id,
                "quantity": item.quantity
            }).execute()
        
        # Clear cart
        supabase.table("cart_items").delete().eq("customer_id", customer_id).execute()
        
        return {"message": "Order created successfully", "order_id": order_id}
    
    raise HTTPException(status_code=400, detail="Order creation failed")

@app.get("/user/orders")
async def get_user_orders(email: str = Depends(verify_token)):
    # Get customer ID
    customer = supabase.table("customers").select("id").eq("email", email).execute()
    if not customer.data:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_id = customer.data[0]["id"]
    
    # Get orders
    result = supabase.table("orders").select("*").eq("customer_id", customer_id).order("created_at", desc=True).execute()
    return result.data