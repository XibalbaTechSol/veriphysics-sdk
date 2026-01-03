
try:
    import c2pa
    print(f"C2PA version: {c2pa.__version__}")
except ImportError as e:
    print(f"Failed to import c2pa: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Check if we can find the certs
import os
cert_path = "backend/certs/ps256.crt"
key_path = "backend/certs/ps256.pem"

if os.path.exists(cert_path) and os.path.exists(key_path):
    print("Certificates found.")
else:
    print("Certificates NOT found.")
