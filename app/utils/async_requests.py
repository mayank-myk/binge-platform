import asyncio
import binascii
import hashlib
import hmac
import os

import requests
from app.utils.config import get_config

service_key = get_config("SERVICE_KEY")
service_id = get_config("SERVICE_ID")


async def get(url, params=None, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: requests.get(
            url, params=params, headers=get_headers_for_internal_request(), **kwargs
        ),
    )


async def post(url, data=None, json=None, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: requests.post(
            url,
            data=data,
            json=json,
            headers=get_headers_for_internal_request(),
            **kwargs,
        ),
    )


def get_headers_for_internal_request():
    nonce, service_signature = generate_hmac_signature()
    headers = {
        "SIMPL-SERVICE-ID": service_id,
        "SIMPL-SERVICE-NONCE": nonce,
        "SIMPL-SERVICE-SIGNATURE": service_signature,
    }
    return headers


def generate_hmac_signature():
    nonce = binascii.hexlify(os.urandom(16)).decode()
    key = f"{nonce}-{service_id}"
    service_key_encode = bytes(service_key, "UTF-8")
    message = bytes(key, "UTF-8")
    digester = hmac.new(service_key_encode, message, hashlib.sha1)
    signature = digester.hexdigest()
    return nonce, signature
