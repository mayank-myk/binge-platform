from typing import Union

from app.models.user_metadata import OnboardingSource, UserMetadata
from app.models.user_metadata import repository as user_metadata_repository
from pydantic import BaseModel


class Eligibility(BaseModel):
    phone_number: str
    referral_eligibility: bool
    transactional_eligibility: bool
    onboarding_eligibility: bool


class ReferralEligibilityService:
    DEFAULT_CREDIT_ELIGIBILITY = False
    DEFAULT_TRANSACTIONAL_ELIGIBILITY = True
    DEFAULT_ONBOARDING_ELIGIBILITY = True
    DEFAULT_REFERRAL_ELIGIBILITY = False

    @classmethod
    def __credit_eligibility(cls, metadata: Union[UserMetadata, None]) -> bool:
        """
        The function returns the eligibility of a user based on the credit lines.

        Returns:
            bool: credit eligibility
        """
        if metadata is None:
            return cls.DEFAULT_CREDIT_ELIGIBILITY
        return metadata.has_gcl or metadata.has_mcl

    @classmethod
    def __transactional_eligibility(cls, metadata: Union[UserMetadata, None]) -> bool:
        """
        The function returns the eligibility of a user based on the transaction status.

        Returns:
            bool: transactional eligibility
        """
        if metadata is None:
            return cls.DEFAULT_TRANSACTIONAL_ELIGIBILITY
        return not metadata.has_transacted

    @classmethod
    def __onboarding_eligibility(cls, metadata: Union[UserMetadata, None]) -> bool:
        """
        The function returns the eligibility of a user based on the source and statues of the onboarding.

        Returns:
            bool: onboarding eligibility
        """
        if metadata is None:
            return cls.DEFAULT_ONBOARDING_ELIGIBILITY
        return not (
            metadata.onboarding_source
            in [OnboardingSource.Android, OnboardingSource.Ios, OnboardingSource.App]
            or metadata.has_completed_onboarding
            or metadata.has_waitlisted_onboarding
        )

    @classmethod
    def __referral_eligibility(cls, metadata: Union[UserMetadata, None]) -> bool:
        credit_eligibility = cls.__credit_eligibility(metadata)
        transactional_eligibility = cls.__transactional_eligibility(metadata)
        onboarding_eligibility = cls.__onboarding_eligibility(metadata)
        return (
            credit_eligibility and transactional_eligibility and onboarding_eligibility
        )

    @classmethod
    async def transaction_eligibility(cls, phone_number: str) -> bool:
        metadata = await user_metadata_repository.get_by_phone_number(
            phone_number=phone_number
        )
        return cls.__transactional_eligibility(metadata)

    @classmethod
    async def eligibility(cls, phone_number: str) -> bool:
        """
        The function returns the eligibility of a user based on the transactional and onboarding eligibility.

        Returns:
            bool: referral eligibility
        """
        metadata = await user_metadata_repository.get_by_phone_number(phone_number)
        return cls.__referral_eligibility(metadata=metadata)

    @classmethod
    async def eligibilities(
        cls, phone_numbers: Union[list[str], set[str]]
    ) -> dict[str, bool]:
        """
        The function returns the eligibility of all the user phone numbers
        based on the transactional and onboarding eligibility.

        Args:
            phone_numbers (Union[list[str], set[str]]): list of phone number in the 10 digit format.

        Returns:
            dict[str, bool]: dictionary with key are phone number and value as the eligibility
        """
        users_metadata = await user_metadata_repository.bulk_get_by_phone_numbers(
            phone_numbers
        )
        eligibilities = {
            metadata.phone_number: cls.__referral_eligibility(metadata)
            for metadata in users_metadata
        }
        for phone_number in phone_numbers:
            if phone_number not in eligibilities:
                eligibilities[phone_number] = cls.DEFAULT_REFERRAL_ELIGIBILITY
        return eligibilities
