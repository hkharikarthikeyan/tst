from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Product(BaseModel):
    name: str
    price: float
    description: str

class Subscription(BaseModel):
    name: str
    price: float
    duration: str
    features: List[str]

class UserSubscription(BaseModel):
    subscription_id: int

class CartItem(BaseModel):
    product_id: int
    quantity: int

class Order(BaseModel):
    items: List[CartItem]
    total_amount: float