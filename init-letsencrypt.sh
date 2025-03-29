#!/bin/bash

if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "Getting SSL certificates for $DOMAIN..."

    certbot certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email $EMAIL \
        -d $DOMAIN

    if [ $? -ne 0 ]; then
        echo "Failed to obtain certificates! Starting without SSL..."
        exec uvicorn app.endpoint:app --host 0.0.0.0 --port 8000
        exit 1
    fi
fi

echo "SSL certificates already exist for $DOMAIN"