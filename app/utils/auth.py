import hashlib
import hmac
import os
import uuid

from app.exceptions.auth import NotAuthorizedRequestException
from app.utils.logger import logger
from fastapi import Header, HTTPException

log = logger()


def _read_service_auth_from_env():
    service_auths = {}
    for k in os.environ:
        if k.startswith("SERVICE_AUTH_CONFIG"):
            service_id, service_key = os.environ[k].split(":")
            service_auths[service_id] = service_key
    return service_auths


def _compute_signature(simpl_service_id, service_key, simpl_service_nonce):
    message = "%s-%s" % (simpl_service_nonce, simpl_service_id)
    return hmac.new(
        bytes(service_key, "UTF-8"), bytes(message, "UTF-8"), hashlib.sha1
    ).hexdigest()


def get_headers(auth_config: str, nonce=str(uuid.uuid4())) -> dict:
    service_id, service_key = os.environ[auth_config].split(":")
    return {
        "SIMPL-SERVICE-ID": service_id,
        "SIMPL-SERVICE-NONCE": nonce,
        "SIMPL-SERVICE-SIGNATURE": _compute_signature(service_id, service_key, nonce),
    }


async def authenticate_request(
    simpl_service_id: str = Header(None),
    simpl_service_nonce: str = Header(None),
    simpl_service_signature: str = Header(None),
):
    if os.getenv("ENABLE_AUTH_FOR_APIS", "1") == "0":
        return True
    if (
        simpl_service_id is None
        or simpl_service_nonce is None
        or simpl_service_signature is None
    ):
        raise NotAuthorizedRequestException(
            service_id=simpl_service_id,
            nonce=simpl_service_nonce,
            signature=simpl_service_signature,
        )
    service_key = _read_service_auth_from_env().get(simpl_service_id, None)
    if (
        service_key is None
        or _compute_signature(simpl_service_id, service_key, simpl_service_nonce)
        != simpl_service_signature
    ):
        raise NotAuthorizedRequestException(
            service_id=simpl_service_id,
            nonce=simpl_service_nonce,
            signature=simpl_service_signature,
        )
