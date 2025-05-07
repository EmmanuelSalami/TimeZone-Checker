# Phone Number Information API

A FastAPI-based API that extracts and provides information about phone numbers worldwide. The API uses the `phonenumbers` library for parsing phone numbers and extracting information like country, region, carrier, and number type.

## Features

- Country detection for 30+ countries
- Region/city information
- Carrier details
- Number type classification (mobile, landline, toll-free, etc.)
- Validity checking
- Format normalization
- Special handling for common country codes (US, UK, Canada, Australia, etc.)
- Robust error handling

## API Endpoints

- `/phone-info?phone_number={number}` - Get detailed information about a phone number
- `/phone-types` - Get mapping of phone number type codes to descriptions

## Countries Covered in Testing

### North America
- United States
- Canada
- Mexico

### Europe
- United Kingdom
- France
- Germany
- Sweden
- Finland
- Czech Republic
- Ireland
- Norway
- Denmark
- Poland
- Hungary
- Austria
- Switzerland
- Belgium
- Portugal
- Greece

### Asia-Pacific
- Australia
- Japan
- South Korea
- China
- India
- Indonesia
- Singapore
- Malaysia
- Thailand
- Philippines
- Vietnam
- Hong Kong
- New Zealand

### Africa & Middle East
- South Africa
- Nigeria
- Egypt
- Morocco
- Turkey
- Saudi Arabia
- Israel
- United Arab Emirates
- Kenya

### South America
- Brazil
- Argentina
- Colombia
- Peru
- Chile
- Venezuela
- Ecuador

## Installation

1. Clone the repository:
```bash
git clone https://github.com/EmmanuelSalami/TimeZone-Checker.git
cd TimeZone-Checker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
uvicorn phone_info_api:app --reload
```

2. Access the API at:
```
http://127.0.0.1:8000/phone-info?phone_number=+1234567890
```

## Testing

The API has been extensively tested with phone numbers from 30+ countries. To run the tests:

```bash
python run_all_tests.py
```

This will run comprehensive tests covering:
- Basic country detection and validation
- Detailed carrier and region information
- Special number types (toll-free, premium)
- Edge cases and error handling
- Different number formats

## Deployment

This API can be deployed to Vercel using the provided configuration files.

## License

MIT 