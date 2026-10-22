#!/bin/sh
# Generate Self-signed SSL Certificate for 192.168.102.129 and localhost
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/server.key \
    -out /etc/nginx/ssl/server.crt \
    -subj "/C=VN/ST=ThaiNguyen/L=ThaiNguyen/O=ICTU/OU=DTC245200964/CN=192.168.102.129" \
    -addext "subjectAltName=DNS:localhost,DNS:crm.local,IP:192.168.102.129,IP:127.0.0.1"
