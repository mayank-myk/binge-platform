from app.exceptions.validation_exceptions import (
    EmptyPhoneNumbersListException,
    ExceedPhoneNumbersListLengthException,
    InvalidPhoneNumberException,
)
from pydantic import BaseModel, validator


class ReferralEligibilityRequest(BaseModel):
    phone_numbers: set[str]

    @validator("phone_numbers")
    def check_phone_numbers_list(cls, values: set[str]):
        if len(values) == 0:
            raise EmptyPhoneNumbersListException()
        if len(values) > 100:
            raise ExceedPhoneNumbersListLengthException(max_length=100)
        return values

    @validator("phone_numbers", each_item=True)
    def check_phone_number_format(cls, value: str) -> str:
        """
        Phone numbers in the contacts should numeric and contain only 10 digits.

        Args:
            value (str): Phone number in the contacts list

        Raises:
            InvalidPhoneNumberException: Validation errors

        Returns:
            str: Returns the value if no errors
        """
        if len(value) != 10 or not value.isnumeric():
            raise InvalidPhoneNumberException(phone_number=value)
        return value
