# Phone Number Information API

A FastAPI-based REST API that provides detailed information about phone numbers worldwide, including country, region, carrier, and more. This API is built using Google's libphonenumber library (phonenumbers Python package).

## Features

- **Country identification**: Identify the country code and country name
- **Region detection**: Where available, get the region/city information
- **Carrier information**: For mobile numbers, identify the carrier (where available)
- **Number type classification**: Distinguish between mobile, landline, toll-free, etc.
- **Formatting**: Get properly formatted international phone numbers
- **Validation**: Check if phone numbers are valid
- **Flexible input formats**: Handle various formats including local formats, international prefixes, etc.

## Installation

### Prerequisites

- Python 3.10 or later
- pip package manager

### Setup

1. Clone this repository
```bash
git clone https://github.com/yourusername/phone-info-api.git
cd phone-info-api
```

2. Create a virtual environment (recommended)
```bash
python -m venv phone_env
```

3. Activate the virtual environment

On Windows:
```bash
phone_env\Scripts\activate
```

On macOS/Linux:
```bash
source phone_env/bin/activate
```

4. Install dependencies
```bash
pip install -r requirements.txt
```

## Running the API

Start the API server with:
```bash
uvicorn phone_info_api:app --reload
```

The API will be available at http://127.0.0.1:8000

## API Documentation

Once the server is running, you can access the automatically generated Swagger documentation at:
```
http://127.0.0.1:8000/docs
```

### Endpoints

#### GET /phone-info

Get detailed information about a phone number.

**Parameters:**
- `phone_number` (required): The phone number to lookup (can be in various formats)
- `default_region` (optional, default="US"): Default region to use if country code is missing

**Response example:**
```json
{
  "country_code": 1,
  "national_number": 4155552671,
  "country": "United States",
  "region": "San Francisco, CA",
  "carrier": "",
  "type": "2",
  "is_valid": true,
  "formatted_number": "+1 415-555-2671"
}
```

#### GET /phone-types

Get a mapping of phone number type codes to their names.

**Response example:**
```json
{
  "0": "FIXED_LINE",
  "1": "MOBILE",
  "2": "FIXED_LINE_OR_MOBILE",
  "3": "TOLL_FREE",
  "..."
}
```

## Testing

The repository includes a test script that demonstrates the API's capabilities with phone numbers from various countries and in different formats:

```bash
python test_phone_numbers.py
```

## Error Handling

The API provides clear error responses for invalid or unparsable numbers:

```json
{
  "detail": {
    "error": "Invalid phone number format",
    "detail": "The provided number could not be parsed."
  }
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [phonenumbers](https://github.com/daviddrysdale/python-phonenumbers) - Python port of Google's libphonenumber
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs 