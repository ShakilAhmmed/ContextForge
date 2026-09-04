#!/bin/sh
set -e

cd "$(dirname "$0")"

DOMAIN="${1:-contextforge.local}"

openssl req -x509 -nodes -newkey rsa:2048 -days 825 \
    -keyout dev.key -out dev.crt \
    -subj "/CN=${DOMAIN}" \
    -addext "subjectAltName=DNS:${DOMAIN}"

echo "wrote dev.crt / dev.key for ${DOMAIN}"
