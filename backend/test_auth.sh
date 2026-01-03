#!/bin/bash
set -e

# 1. Register
echo ">>> Registering..."
curl -s -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@veriphysics.com", "password": "password123"}'
echo ""

# 2. Login
echo ">>> Logging in..."
TOKEN_RESP=$(curl -s -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test@veriphysics.com&password=password123")
echo "Response: $TOKEN_RESP"
TOKEN=$(echo $TOKEN_RESP | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3. Create API Key
echo ">>> Creating API Key..."
KEY_RESP=$(curl -s -X POST "http://localhost:8000/api-keys" \
     -H "Authorization: Bearer $TOKEN")
echo "Response: $KEY_RESP"
API_KEY=$(echo $KEY_RESP | python3 -c "import sys, json; print(json.load(sys.stdin)['api_key'])")

# 4. Verify Content (Mock)
echo ">>> Verifying content with API Key..."
touch video.mp4 gyro.csv
curl -v -X POST "http://localhost:8000/verify" \
     -H "x-api-key: $API_KEY" \
     -F "video=@video.mp4" \
     -F "gyro=@gyro.csv"
rm video.mp4 gyro.csv
echo ""
