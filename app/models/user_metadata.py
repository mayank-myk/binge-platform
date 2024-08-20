from typing import Union

from app.exceptions.user_metadata_repository import (
    DeleteGlobalCreditLineException,
    DeleteMerchantCreditLineException,
    FetchManyUserMetadataException,
    FetchOneUserMetadataException,
    UpsertGlobalCreditLineException,
    UpsertMerchantCreditLineException,
    UpsertOnboardingCompletedStatusException,
    UpsertOnboardingSourceException,
    UpsertOnboardingWaitlistedStatusException,
    UpsertTransactedStatusException,
)
from app.models import OnboardingSource, UserMetadata
from app.utils.logger import logger
from app.utils.postgresdb import prod_others_db_reader, prod_others_db_writer
from app.utils.singleton import Singleton

_log = logger()


class __UserMetadataRepo(metaclass=Singleton):
    UPSERT_ONBOARDING_SOURCE_BY_PHONE_NUMBER = """INSERT INTO user_metadata (phone_number, onboarding_source)
              VALUES(%(phone_number)s,%(onboarding_source)s)
              ON CONFLICT (phone_number)
              DO UPDATE SET onboarding_source = EXCLUDED.onboarding_source;
              """
    UPSERT_ONBOARDING_COMPLETED_STATUS_BY_PHONE_NUMBER = """INSERT INTO user_metadata (phone_number, 
                    has_completed_onboarding) VALUES(%(phone_number)s,true) ON CONFLICT (phone_number) DO UPDATE SET 
                    has_completed_onboarding = true; 
    """
    UPSERT_ONBOARDING_WAITLISTED_STATUS_BY_PHONE_NUMBER = """INSERT INTO user_metadata (phone_number, 
                    has_waitlisted_onboarding) VALUES(%(phone_number)s,true) ON CONFLICT (phone_number) DO UPDATE SET 
                    has_waitlisted_onboarding = true; 
    """
    UPSERT_HAS_TRANSACTED_STATUS_BY_PHONE_NUMBER = """INSERT INTO user_metadata (phone_number, has_transacted)
                      VALUES(%(phone_number)s,true)
                      ON CONFLICT (phone_number)
                      DO UPDATE SET has_transacted = true;
            """
    GET_USER_METADATA_BY_PHONE_NUMBER = """SELECT phone_number, has_transacted, onboarding_source, 
                    has_completed_onboarding, has_waitlisted_onboarding, global_credit_lines, merchant_credit_lines FROM 
                    user_metadata WHERE phone_number = %(phone_number)s; 
    """
    BULK_GET_USER_METADATA_BY_PHONE_NUMBERS = """SELECT phone_number, has_transacted, onboarding_source, 
                    has_completed_onboarding, has_waitlisted_onboarding, global_credit_lines, merchant_credit_lines FROM 
                    user_metadata WHERE phone_number IN %(phone_number)s; 
    """
    DELETE_GLOBAL_CREDIT_LINE_BY_PHONE_NUMBER = """UPDATE user_metadata 
                    SET global_credit_lines = array_remove(global_credit_lines, %(global_credit_line)s) WHERE phone_number = %(phone_number)s;
    """
    DELETE_MERCHANT_CREDIT_LINE_BY_PHONE_NUMBER = """UPDATE user_metadata SET merchant_credit_lines = array_remove(
                    merchant_credit_lines, %(merchant_credit_line)s) WHERE phone_number = %(phone_number)s; 
    """
    UPSERT_GLOBAL_CREDIT_LINE_BY_PHONE_NUMBER = """INSERT INTO user_metadata (phone_number, global_credit_lines) 
                    VALUES(%(phone_number)s,%(global_credit_lines)s) ON CONFLICT (phone_number) DO UPDATE SET global_credit_lines = 
                    array(select distinct unnest(user_metadata.global_credit_lines || excluded.global_credit_lines)); 
    """
    UPSERT_MERCHANT_CREDIT_LINE_BY_PHONE_NUMBER = """INSERT INTO user_metadata (phone_number, merchant_credit_lines) 
                    VALUES(%(phone_number)s,%(merchant_credit_lines)s) ON CONFLICT (phone_number) DO UPDATE SET global_credit_lines = 
                    array(select distinct unnest(user_metadata.merchant_credit_lines || excluded.merchant_credit_lines)); 
    """

    async def upsert_onboarding_source(
        self, phone_number: str, onboarding_source: OnboardingSource
    ) -> None:
        try:
            prod_others_db_writer.execute(
                self.UPSERT_ONBOARDING_SOURCE_BY_PHONE_NUMBER,
                {
                    "phone_number": phone_number,
                    "onboarding_source": onboarding_source.value,
                },
            )
        except Exception as ex:
            raise UpsertOnboardingSourceException(
                ex, phone_number, onboarding_source=str(onboarding_source.value)
            )

    async def upsert_onboarding_completed_status(self, phone_number: str) -> None:
        try:
            prod_others_db_writer.execute(
                self.UPSERT_ONBOARDING_COMPLETED_STATUS_BY_PHONE_NUMBER,
                {"phone_number": phone_number},
            )
        except Exception as ex:
            raise UpsertOnboardingCompletedStatusException(ex, phone_number)

    async def upsert_onboarding_waitlisted_status(self, phone_number: str) -> None:
        try:
            prod_others_db_writer.execute(
                self.UPSERT_ONBOARDING_WAITLISTED_STATUS_BY_PHONE_NUMBER,
                {"phone_number": phone_number},
            )
        except Exception as ex:
            raise UpsertOnboardingWaitlistedStatusException(ex, phone_number)

    async def upsert_has_transacted(self, phone_number: str) -> None:
        try:
            prod_others_db_writer.execute(
                self.UPSERT_HAS_TRANSACTED_STATUS_BY_PHONE_NUMBER,
                {"phone_number": phone_number},
            )
        except Exception as ex:
            raise UpsertTransactedStatusException(ex, phone_number)

    async def upsert_global_credit_line(
        self, phone_number: str, credit_line: str
    ) -> None:
        try:
            prod_others_db_writer.execute(
                self.UPSERT_GLOBAL_CREDIT_LINE_BY_PHONE_NUMBER,
                {
                    "phone_number": phone_number,
                    "global_credit_lines": [credit_line],
                },
            )
        except Exception as ex:
            raise UpsertGlobalCreditLineException(ex, phone_number, credit_line)

    async def upsert_merchant_credit_line(
        self, phone_number: str, credit_line: str
    ) -> None:
        try:
            prod_others_db_writer.execute(
                self.UPSERT_MERCHANT_CREDIT_LINE_BY_PHONE_NUMBER,
                {
                    "phone_number": phone_number,
                    "merchant_credit_lines": [credit_line],
                },
            )
        except Exception as ex:
            raise UpsertMerchantCreditLineException(ex, phone_number, credit_line)

    async def remove_global_credit_line(
        self, phone_number: str, credit_line: str
    ) -> None:
        try:
            prod_others_db_writer.execute(
                self.DELETE_GLOBAL_CREDIT_LINE_BY_PHONE_NUMBER,
                {
                    "phone_number": phone_number,
                    "global_credit_line": credit_line,
                },
            )
        except Exception as ex:
            raise DeleteGlobalCreditLineException(ex, phone_number, credit_line)

    async def remove_merchant_credit_line(
        self, phone_number: str, credit_line: str
    ) -> None:
        try:
            prod_others_db_writer.execute(
                self.DELETE_MERCHANT_CREDIT_LINE_BY_PHONE_NUMBER,
                {
                    "phone_number": phone_number,
                    "merchant_credit_line": credit_line,
                },
            )
        except Exception as ex:
            raise DeleteMerchantCreditLineException(ex, phone_number, credit_line)

    async def get_by_phone_number(self, phone_number: str) -> Union[UserMetadata, None]:
        try:
            record = prod_others_db_reader.fetch_one(
                self.GET_USER_METADATA_BY_PHONE_NUMBER, {"phone_number": phone_number}
            )
            if record is not None:
                user_metadata = UserMetadata(
                    phone_number=phone_number,
                    has_transacted=record[1],
                    onboarding_source=record[2]
                    if record[2] is None
                    else OnboardingSource(record[2]),
                    has_completed_onboarding=record[3],
                    has_waitlisted_onboarding=record[4],
                    global_credit_lines=record[5],
                    merchant_credit_lines=record[6],
                )
                return user_metadata
            _log.info("No record found for phone number {}".format(phone_number))
            return None
        except Exception as ex:
            raise FetchOneUserMetadataException(ex, phone_number)

    async def bulk_get_by_phone_numbers(
        self, phone_numbers: Union[list[str], set[str]]
    ) -> list[UserMetadata]:
        response = []
        if len(phone_numbers) == 0:
            return []
        try:
            records = prod_others_db_reader.fetch_all(
                self.BULK_GET_USER_METADATA_BY_PHONE_NUMBERS,
                {"phone_number": tuple(phone_numbers)},
            )

            if records is None:
                _log.info("No record found for phone numbers")
                return []

            for record in records:
                user_metadata = UserMetadata(
                    phone_number=record[0],
                    has_transacted=record[1],
                    onboarding_source=record[2]
                    if record[2] is None
                    else OnboardingSource(record[2]),
                    has_completed_onboarding=record[3],
                    has_waitlisted_onboarding=record[4],
                    global_credit_lines=record[5],
                    merchant_credit_lines=record[6],
                )
                response.append(user_metadata)

            return response
        except Exception as ex:
            raise FetchManyUserMetadataException(ex, phone_numbers)


repository = __UserMetadataRepo()
