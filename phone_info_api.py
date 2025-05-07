from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import phonenumbers
from phonenumbers import geocoder, carrier, number_type
from phonenumbers.phonenumberutil import NumberParseException
from typing import Optional, Union

app = FastAPI(title="Phone Number Information API",
              description="API that provides detailed information about phone numbers worldwide",
              version="1.0.0")

class PhoneInfoResponse(BaseModel):
    country_code: int
    national_number: int
    country: str
    region: str
    carrier: str
    type: str
    is_valid: bool
    formatted_number: str

class ErrorResponse(BaseModel):
    error: str
    detail: str = ""

@app.get("/", include_in_schema=False)
async def read_root():
    return {"message": "Welcome to the Phone Number Information API", 
            "documentation": "/docs",
            "example": "/phone-info?phone_number=+14155552671"}

@app.get("/phone-info", 
         response_model=Union[PhoneInfoResponse, ErrorResponse], 
         responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def phone_info(phone_number: str = Query(..., description="Phone number in international format, e.g. +14155552671"), 
               default_region: str = Query("US", description="Default region if country code is missing")):
    try:
        # Clean and normalize the phone number
        cleaned_number = phone_number.strip()
        
        # Handle international prefix (00) instead of +
        if cleaned_number.startswith("00"):
            cleaned_number = "+" + cleaned_number[2:]
            
        # Try to parse the number
        try:
            parsed = phonenumbers.parse(cleaned_number, default_region)
        except NumberParseException:
            # If parsing fails with the given format, try to see if it's a local number
            try:
                if not cleaned_number.startswith("+"):
                    parsed = phonenumbers.parse(cleaned_number, default_region)
                else:
                    raise
            except:
                return ErrorResponse(
                    error="Unable to parse phone number",
                    detail="The provided number could not be parsed. Please check the format."
                )
        
        # Validate the number
        is_valid = phonenumbers.is_valid_number(parsed)
        
        # Even if not fully valid, we can still return some information
        # but we'll indicate it's not valid
        number_type_value = number_type(parsed)
        
        # Get the information for the number
        return PhoneInfoResponse(
            country_code=parsed.country_code,
            national_number=parsed.national_number,
            country=geocoder.country_name_for_number(parsed, "en") or "Unknown",
            region=geocoder.description_for_number(parsed, "en") or "Unknown",
            carrier=carrier.name_for_number(parsed, "en") or "",
            type=str(number_type_value),
            is_valid=is_valid,
            formatted_number=phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        )
        
    except NumberParseException as e:
        return ErrorResponse(
            error="Invalid phone number format",
            detail=str(e)
        )
    except Exception as e:
        return ErrorResponse(
            error="Server error processing phone number",
            detail=str(e)
        )

# Add a readable translation for phone number types
@app.get("/phone-types", include_in_schema=True)
async def phone_types():
    return {
        "0": "FIXED_LINE",
        "1": "MOBILE",
        "2": "FIXED_LINE_OR_MOBILE",
        "3": "TOLL_FREE",
        "4": "PREMIUM_RATE",
        "5": "SHARED_COST",
        "6": "VOIP",
        "7": "PERSONAL_NUMBER",
        "8": "PAGER",
        "9": "UAN",
        "10": "VOICEMAIL",
        "27": "EMERGENCY",
        "28": "SHORT_CODE",
        "29": "STANDARD_RATE",
        "30": "CARRIER_SPECIFIC"
    } 