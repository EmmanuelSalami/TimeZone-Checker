from fastapi import FastAPI, Query, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import phonenumbers
from phonenumbers import geocoder, carrier, number_type
from phonenumbers.phonenumberutil import NumberParseException
from typing import Optional, Union, Callable
import re
import urllib.parse

app = FastAPI(title="Phone Number Information API",
              description="API that provides detailed information about phone numbers worldwide",
              version="1.0.0")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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

def normalize_phone_number(phone_number: str) -> str:
    """
    Normalize phone number input to ensure it's properly formatted
    with country code regardless of how it was entered
    """
    # First decode URL encoding if present
    try:
        phone_number = urllib.parse.unquote(phone_number)
    except:
        pass  # If it's not URL encoded, that's fine
    
    # Clean and normalize the phone number
    cleaned_number = phone_number.strip()
    
    # Replace any non-breaking spaces or unusual whitespace
    cleaned_number = re.sub(r'\s+', ' ', cleaned_number)
    
    # Ensure "+" is present for international format
    if not cleaned_number.startswith("+"):
        # Check if it starts with "00" (international prefix)
        if cleaned_number.startswith("00"):
            cleaned_number = "+" + cleaned_number[2:]
        # Check if it could be an international number without "+"
        # UK numbers (44)
        elif re.match(r'^44\d{10}', cleaned_number):
            cleaned_number = "+" + cleaned_number
        # US/Canada (1)
        elif re.match(r'^1\d{10}', cleaned_number):
            cleaned_number = "+" + cleaned_number
        # Australian numbers (61)
        elif re.match(r'^61\d{9}', cleaned_number):
            cleaned_number = "+" + cleaned_number
        # Nigerian numbers (234)
        elif re.match(r'^234\d{10}', cleaned_number):
            cleaned_number = "+" + cleaned_number
    
    # Remove common formatting characters from phone numbers
    cleaned_number = re.sub(r'[\(\)\-\.\s]', '', cleaned_number)
    
    # Re-add "+" if it was stripped
    if not cleaned_number.startswith("+") and any(cleaned_number.startswith(cc) for cc in 
                                                ["1", "44", "61", "234", "33", "49", "86", "91"]):
        cleaned_number = "+" + cleaned_number
        
    return cleaned_number

# Dependency to preprocess phone number parameter
async def get_normalized_phone_number(
    phone_number: str = Query(..., description="Phone number in any format with country code")
) -> str:
    return normalize_phone_number(phone_number)

@app.get("/", include_in_schema=False)
async def read_root():
    return {"message": "Welcome to the Phone Number Information API", 
            "documentation": "/docs",
            "example": "/phone-info?phone_number=+14155552671"}

@app.get("/phone-info", 
         response_model=Union[PhoneInfoResponse, ErrorResponse], 
         responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def phone_info(
    phone_number: str = Depends(get_normalized_phone_number),
    default_region: str = Query("US", description="Default region if country code is missing")
):
    try:
        # Clean and normalize the phone number (now handled by dependency)
        cleaned_number = phone_number
        
        # Before parsing, detect and enforce country code for common formats
        # Handle UK numbers specifically
        if re.match(r'^\+44|^44', cleaned_number):
            default_region = "GB"  # Force UK parsing
        # Handle other specific cases as needed
        elif re.match(r'^\+1|^1', cleaned_number) and len(cleaned_number) >= 11:
            default_region = "US"  # Force US parsing
        # Handle Australian numbers
        elif re.match(r'^\+61|^61', cleaned_number):
            default_region = "AU"  # Force Australian parsing
        # Handle Nigerian numbers
        elif re.match(r'^\+234|^234', cleaned_number):
            default_region = "NG"  # Force Nigerian parsing
            
        # Try to parse the number
        try:
            parsed = phonenumbers.parse(cleaned_number, default_region)
        except NumberParseException:
            # If parsing fails with the given format, try more aggressively
            try:
                # If it looks like a UK number but wasn't properly formatted
                if re.search(r'44\d{10}', cleaned_number):
                    # Try to reformat as UK
                    uk_number = "+44" + re.search(r'44(\d{10})', cleaned_number).group(1)
                    parsed = phonenumbers.parse(uk_number, "GB")
                # If it looks like an Australian mobile but wasn't properly formatted
                elif re.search(r'61\d{9}', cleaned_number):
                    # Try to reformat as Australian
                    au_number = "+61" + re.search(r'61(\d{9})', cleaned_number).group(1)
                    parsed = phonenumbers.parse(au_number, "AU")
                else:
                    # Last resort: try with the default region
                    parsed = phonenumbers.parse(cleaned_number, default_region)
            except:
                return ErrorResponse(
                    error="Unable to parse phone number",
                    detail=f"The provided number '{phone_number}' could not be parsed. Please check the format and include the country code."
                )
        
        # Double-check if the number has a recognized country code
        if parsed.country_code == 0:
            return ErrorResponse(
                error="Invalid country code",
                detail="The phone number does not have a recognized country code."
            )
        
        # Validate the number
        is_valid = phonenumbers.is_valid_number(parsed)
        
        # Even if not fully valid, we can still return some information
        # but we'll indicate it's not valid
        number_type_value = number_type(parsed)
        
        # Get country and region
        country = geocoder.country_name_for_number(parsed, "en")
        region = geocoder.description_for_number(parsed, "en")
        
        # Special handling for Australian numbers
        if parsed.country_code == 61:
            # Ensure country is set correctly
            country = "Australia"
            
            # For Australian mobile numbers (start with 4)
            mobile_prefix = str(parsed.national_number)
            if mobile_prefix.startswith('4'):
                # If geocoder doesn't provide a region
                if not region or region == "Unknown":
                    region = "Australia Mobile"
            
            # For specific area codes
            area_code = str(parsed.national_number)[:1]
            if area_code == '2' and (not region or region == "Unknown"):
                region = "Sydney/NSW"
            elif area_code == '3' and (not region or region == "Unknown"):
                region = "Melbourne/Victoria"
            elif area_code == '7' and (not region or region == "Unknown"):
                region = "Queensland"
            elif area_code == '8' and (not region or region == "Unknown"):
                region = "Adelaide/Perth"
        
        # Get the information for the number
        return PhoneInfoResponse(
            country_code=parsed.country_code,
            national_number=parsed.national_number,
            country=country or "Unknown",
            region=region or "Unknown",
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