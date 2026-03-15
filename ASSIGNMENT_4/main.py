from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import HTTPException

app = FastAPI()

# ---------------- PRODUCTS ----------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

# ---------------- STORAGE ----------------

cart = []
orders = []


# ---------------- ADD TO CART ----------------

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = None

    for p in products:
        if p["id"] == product_id:
            product = p
            break

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock"
        )

    # check if item already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * product["price"]

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    subtotal = product["price"] * quantity

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }


# ---------------- VIEW CART ----------------

@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": total
    }


# ---------------- REMOVE ITEM ----------------

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}

    raise HTTPException(status_code=404, detail="Item not found in cart")


# ---------------- CHECKOUT MODEL ----------------

class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str


# ---------------- CHECKOUT ----------------

@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):

    # Empty cart validation
    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    placed_orders = []

    for item in cart:
        order = {
            "order_id": len(orders) + 1,
            "customer_name": data.customer_name,
            "delivery_address": data.delivery_address,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }

        orders.append(order)
        placed_orders.append(order)

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": len(placed_orders),
        "orders": placed_orders
    }
# ---------------- VIEW ORDERS ----------------

@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }
