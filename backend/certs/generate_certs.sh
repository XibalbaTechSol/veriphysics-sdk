#!/bin/bash
mkdir -p backend/certs
cd backend/certs

# Generate a private key (ES256)
openssl ecparam -genkey -name prime256v1 -out ps256_raw.pem
openssl pkcs8 -topk8 -nocrypt -in ps256_raw.pem -out ps256.pem

# Generate a certificate signing request (CSR)
openssl req -new -key ps256.pem -out ps256.csr -subj "/C=US/ST=State/L=City/O=VeriPhysics/CN=VeriPhysics Dev"

# Generate a self-signed certificate
openssl x509 -req -days 365 -in ps256.csr -signkey ps256.pem -out ps256.crt

echo "Certificates generated in backend/certs/"
ls -l ps256.pem ps256.crt
