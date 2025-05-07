import asyncio
import aiohttp
import json
from tabulate import tabulate

# List of diverse phone numbers from different countries and regions
phone_numbers = [
    # North America
    "+14155552671",     # US - San Francisco, CA
    "+16175551212",     # US - Boston, MA
    "+12125551234",     # US - New York, NY
    "+13105551234",     # US - Los Angeles, CA
    "+14042341234",     # US - Atlanta, GA
    "+12815551234",     # US - Houston, TX
    "+16137371111",     # Canada - Ottawa
    "+15146261234",     # Canada - Montreal
    "+16042571234",     # Canada - Vancouver
    "+17876661234",     # Puerto Rico

    # Cayman Islands
    "+13459496000",     # Cayman Islands - Mobile
    "+13456231234",     # Cayman Islands - Fixed Line
    "+13459271234",     # Cayman Islands
    
    # Nigeria
    "+2348123456789",   # Nigeria - Mobile
    "+2349012345678",   # Nigeria - Mobile
    "+2347023456789",   # Nigeria - MTN Mobile
    "+2348173456789",   # Nigeria - Airtel Mobile
    "+23490123456",     # Nigeria - Lagos
    "+23470123456",     # Nigeria - Abuja
    
    # UK and Ireland
    "+447911123456",    # UK - Mobile
    "+442071234567",    # UK - London
    "+441314960000",    # UK - Edinburgh
    "+35316871234",     # Ireland - Dublin
    
    # Asia
    "+81345678901",     # Japan - Tokyo
    "+818012345678",    # Japan - Mobile
    "+8618611112222",   # China - Mobile
    "+861012345678",    # China - Beijing
    "+862012345678",    # China - Guangzhou
    "+85221234567",     # Hong Kong
    "+919876543210",    # India - Mobile
    "+912212345678",    # India - Mumbai
    "+6590123456",      # Singapore - Mobile
    "+6565123456",      # Singapore - Fixed Line
    "+821012345678",    # South Korea - Mobile
    "+82212345678",     # South Korea - Seoul
    
    # Middle East
    "+971501234567",    # UAE - Mobile
    "+97142123456",     # UAE - Dubai
    "+96612345678",     # Saudi Arabia - Riyadh
    "+9613123456",      # Lebanon - Mobile
    
    # Europe
    "+33123456789",     # France - Paris
    "+4917612345678",   # Germany - Mobile
    "+493012345678",    # Germany - Berlin
    "+390212345678",    # Italy - Milan
    "+34612345678",     # Spain - Mobile
    "+3491123456",      # Spain - Madrid
    "+46812345678",     # Sweden - Stockholm
    
    # South America
    "+551123456789",    # Brazil - São Paulo
    "+5491112345678",   # Argentina - Mobile
    "+56212345678",     # Chile - Santiago
    "+573123456789",    # Colombia - Mobile
    
    # Africa
    "+27211234567",     # South Africa - Cape Town
    "+27110123456",     # South Africa - Johannesburg
    "+20221234567",     # Egypt - Cairo
    "+25411234567",     # Kenya - Nairobi
    "+212522123456",    # Morocco - Casablanca
    
    # Oceania
    "+61261234567",     # Australia - Canberra
    "+61412345678",     # Australia - Mobile
    "+6421123456",      # New Zealand - Mobile
    "+649123456",       # New Zealand - Auckland
    
    # Edge cases and formatting variations
    "(415) 555-2671",   # US format without +
    "00447911123456",   # International prefix instead of +
    "+44 (0) 7911 123456",  # UK with spaces and local prefix
    "+52 1 55 1234 5678",   # Mexico mobile with spaces
    "091 123-4567",     # Japan local format
    
    # Potential error cases
    "+999999999",       # Invalid country code
    "12345",            # Too short
    "+1234567890123456789", # Too long
    "abcdefghij",       # Non-numeric
    "+1234+5678"        # Invalid format
]

# Function to test each number
async def test_phone_numbers(base_url, numbers):
    results = []
    
    # Set up async HTTP session
    async with aiohttp.ClientSession() as session:
        # Get phone type descriptions
        try:
            async with session.get(f"{base_url}/phone-types") as response:
                if response.status == 200:
                    phone_types = await response.json()
                else:
                    phone_types = {}
        except Exception:
            phone_types = {}
        
        # Test each phone number concurrently
        tasks = []
        for number in numbers:
            tasks.append(test_single_number(session, base_url, number, phone_types))
        
        # Gather all results
        results = await asyncio.gather(*tasks)
    
    return results

async def test_single_number(session, base_url, number, phone_types):
    try:
        # Prepare the number for URL (encode + and spaces)
        encoded_number = number.replace("+", "%2B").replace(" ", "%20")
        
        # Make API request
        async with session.get(f"{base_url}/phone-info?phone_number={encoded_number}") as response:
            # Process response
            response_data = await response.json()
            
            if response.status == 200:
                # Check if it's an error response
                if "error" in response_data:
                    return [number, "ERROR", response_data.get("error", "Unknown error"), "", "", "", "", ""]
                
                # Get readable type
                type_code = response_data.get("type", "")
                type_name = phone_types.get(type_code, type_code)
                
                return [
                    number, 
                    response_data.get("country_code", "N/A"),
                    response_data.get("country", "N/A"),
                    response_data.get("region", "N/A"),
                    response_data.get("carrier", "N/A") or "N/A",
                    type_name,
                    "✓" if response_data.get("is_valid", False) else "✗",
                    response_data.get("formatted_number", "")
                ]
            else:
                error_msg = response_data.get("error", f"HTTP {response.status}")
                return [number, "ERROR", error_msg, "", "", "", "", ""]
    except Exception as e:
        return [number, "EXCEPTION", str(e), "", "", "", "", ""]

# Run the tests
async def main():
    api_url = "http://127.0.0.1:8000"
    
    print("Testing phone number API with diverse examples...\n")
    
    results = await test_phone_numbers(api_url, phone_numbers)
    
    # Display results in a table
    headers = ["Phone Number", "Country Code", "Country", "Region", "Carrier", "Type", "Valid", "Formatted"]
    print(tabulate(results, headers=headers, tablefmt="grid"))
    
    # Count successful and failed cases
    successful = sum(1 for r in results if r[1] != "ERROR" and r[1] != "EXCEPTION")
    errors = len(results) - successful
    valid_nums = sum(1 for r in results if r[1] != "ERROR" and r[1] != "EXCEPTION" and r[6] == "✓")
    
    # Print statistics by country
    countries = {}
    for r in results:
        if r[1] != "ERROR" and r[1] != "EXCEPTION":
            country = r[2]
            countries[country] = countries.get(country, 0) + 1
    
    print("\n=== Countries Covered ===")
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
        print(f"{country}: {count} numbers")
    
    print(f"\nSummary: {successful} successful ({valid_nums} valid numbers), {errors} errors/exceptions")
    print(f"Coverage: {len(countries)} countries/regions")

    # Save results to a JSON file for reference
    with open("phone_test_results.json", "w") as f:
        json_results = []
        for result in results:
            if result[1] not in ["ERROR", "EXCEPTION"]:
                json_results.append({
                    "phone_number": result[0],
                    "country_code": result[1],
                    "country": result[2],
                    "region": result[3],
                    "carrier": result[4], 
                    "type": result[5],
                    "valid": result[6] == "✓",
                    "formatted": result[7]
                })
            else:
                json_results.append({
                    "phone_number": result[0],
                    "error": result[2]
                })
        json.dump(json_results, f, indent=2)
    
    print("Results saved to phone_test_results.json")

if __name__ == "__main__":
    asyncio.run(main()) 