import requests

# Test if routes exist
base_url = "http://localhost:8000"

# Test basic routes
try:
    response = requests.get(f"{base_url}/test")
    print(f"Test endpoint: {response.status_code}")
except:
    print("Test endpoint failed")

try:
    response = requests.get(f"{base_url}/user/subscriptions")
    print(f"User subscriptions: {response.status_code}")
except:
    print("User subscriptions failed")

try:
    response = requests.get(f"{base_url}/debug/customers")
    print(f"Debug customers: {response.status_code}")
except:
    print("Debug customers failed")

# Check if server is running
try:
    response = requests.get(f"{base_url}/docs")
    print(f"FastAPI docs: {response.status_code}")
except:
    print("Server not responding")