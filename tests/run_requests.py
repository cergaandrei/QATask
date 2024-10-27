# run_requests.py
from requests_to_validate.all_orders import get_all_orders_router
from requests_to_validate.cancel_order import get_cancel_order_router
from requests_to_validate.create_order import get_create_order_router
from requests_to_validate.specific_order import get_specific_order_router

def validate_all_orders(orders_db):
    router = get_all_orders_router(orders_db)  # Pass orders_db
    orders = router.routes[0].endpoint()  # Access the get_orders function directly
    assert isinstance(orders, list)  # Check that the response is a list

def validate_cancel_order(orders_db, manager):
    router = get_cancel_order_router(orders_db, manager)
    # First, create an order
    create_order_function = get_create_order_router(orders_db, manager).routes[0].endpoint
    order = create_order_function()
    order_id = order['id']

    # Now cancel that order
    cancel_order_function = router.routes[0].endpoint
    cancel_response = cancel_order_function(order_id)
    assert cancel_response["message"] == f"Order {order_id} cancelled"
    assert orders_db[order_id]["status"] == "CANCELLED"

def validate_create_order(orders_db, manager):
    router = get_create_order_router(orders_db, manager)
    create_order_function = router.routes[0].endpoint
    response = create_order_function()
    assert response["status"] == "PENDING"
    assert "id" in response

def validate_specific_order(orders_db):
    router = get_specific_order_router(orders_db)
    # Simulate creating an order for retrieval
    orders_db[1] = {"id": 1, "status": "PENDING"}

    specific_order_function = router.routes[0].endpoint
    order = specific_order_function(1)  # Get order with ID 1

    assert order['id'] == 1  # Check that the returned order matches the created one

if __name__ == "__main__":
    print("This script is meant to be imported for running validations.")
