"""
Internal Error codes
NOTE: IT'S AN APPEND ONLY FILE
"""

__BASE_STRING = "REF_RECOM"
INTERNAL_SERVER_ERROR = f"{__BASE_STRING}_0"
MISSING_REQUIRED_FIELD_ERROR = f"{__BASE_STRING}_1"
INVALID_PHONE_NUMBER_ERROR = f"{__BASE_STRING}_2"
EMPTY_PHONE_NUMBERS_LIST_ERROR = f"{__BASE_STRING}_3"
EXCEED_PHONE_NUMBERS_LIST_LENGTH_ERROR = f"{__BASE_STRING}_4"

INVALID_EVENT_PAYLOAD = f"{__BASE_STRING}_4"

USER_CLIENT_GENERIC_ERROR = f"{__BASE_STRING}_5"
USER_NOT_FOUND = f"{__BASE_STRING}_6"
USER_PHONE_NUMBER_NOT_FOUND = f"{__BASE_STRING}_7"

UPSERT_ONBOARDING_SOURCE_EXCEPTION = f"{__BASE_STRING}_8"
UPSERT_ONBOARDING_COMPLETED_STATUS_EXCEPTION = f"{__BASE_STRING}_9"
UPSERT_ONBOARDING_WAITLISTED_STATUS_EXCEPTION = f"{__BASE_STRING}_10"
UPSERT_TRANSACTED_STATUS_EXCEPTION = f"{__BASE_STRING}_11"
UPSERT_GCL_EXCEPTION = f"{__BASE_STRING}_12"
UPSERT_MCL_EXCEPTION = f"{__BASE_STRING}_13"
DELETE_GCL_EXCEPTION = f"{__BASE_STRING}_14"
DELETE_MCL_EXCEPTION = f"{__BASE_STRING}_15"
FETCH_ONE_EXCEPTION = f"{__BASE_STRING}_16"
FETCH_MANY_EXCEPTION = f"{__BASE_STRING}_17"

# Infrastructure Error Codes
KAFKA_POLL_MESSAGE_ERROR = f"{__BASE_STRING}_INF1"
PSQL_CONNECTION_POLL_ERROR = f"{__BASE_STRING}_INF2"
PSQL_CONNECTION_ERROR = f"{__BASE_STRING}_INF3"
SERVER_NOT_HEALTHY = f"{__BASE_STRING}_INF4"
NOT_AUTHORIZED_REQUEST = f"{__BASE_STRING}_INF5"
