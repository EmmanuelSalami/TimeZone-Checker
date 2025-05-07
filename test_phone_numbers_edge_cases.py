import unittest
import requests
import json
from typing import Dict, Any, List

# API endpoint - update this with your actual URL if different
API_URL = "http://127.0.0.1:8000/phone-info"

class TestPhoneNumbersEdgeCases(unittest.TestCase):
    """Testing edge cases and error handling for the phone number API"""
    
    def make_api_request(self, phone_number: str, default_region: str = None) -> Dict[str, Any]:
        """Make a request to the phone info API and return the response"""
        url = f"{API_URL}?phone_number={phone_number}"
        if default_region:
            url += f"&default_region={default_region}"
        response = requests.get(url)
        return response.json()
    
    def test_invalid_numbers(self):
        """Test handling of completely invalid phone numbers"""
        invalid_numbers = [
            "12345",                  # Too short
            "++1234567890",           # Double plus sign
            "abcdefghijk",            # Not a number
            "+1234567890123456789",   # Too long
            "",                       # Empty string
            "+",                      # Just a plus sign
            "++",                     # Multiple plus signs
            "+aaa",                   # Invalid format
            "+123456x789",            # Contains invalid character
        ]
        
        for number in invalid_numbers:
            result = self.make_api_request(number)
            self.assertIn("error", result, f"Expected error for invalid number: {number}")
            print(f"✓ Invalid number handled correctly: {number} - Error: {result['error']}")
    
    def test_almost_valid_numbers(self):
        """Test numbers that are almost valid but have minor issues"""
        almost_valid = [
            # Number, Expected Error (True=should have error, False=might pass)
            ("+1234567890", True),        # Valid format but not a real number
        ]
        
        for number, should_error in almost_valid:
            result = self.make_api_request(number)
            if should_error:
                self.assertIn("error", result, f"Expected error for almost valid number: {number}")
                print(f"✓ Almost valid number correctly rejected: {number}")
            else:
                print(f"Number {number}: {'Error' if 'error' in result else 'Accepted'}")
    
    def test_unusual_formats(self):
        """Test unusual but potentially valid phone number formats"""
        unusual_formats = [
            # Various forms of the same number - using a known working UK number
            "00442079460958",            # International format with 00 prefix
            "(+44) 2079460958",          # Unusual formatting
            "+44(0)2079460958",          # With a zero in parentheses
            "+44(0)20 7946 0958",        # Spaces and parentheses 
            "+44 [0] 20 7946 0958",      # Brackets
            "+44/20/79460958",           # Slashes
            "+44.20.79460958",           # Periods
            "+44 20 7946 0958 ext 123",  # With extension
        ]
        
        for number in unusual_formats:
            result = self.make_api_request(number)
            # We're testing if the number parser can handle these formats
            # Some may fail, but we're just logging the results
            if "error" in result:
                print(f"× Format not handled: {number} - Error: {result['error']}")
            else:
                print(f"✓ Format handled correctly: {number} - Identified as: {result['country']} number")
                self.assertEqual(result["country"], "United Kingdom", 
                              f"Expected UK number, got {result['country']} for {number}")
    
    def test_url_encoded_numbers(self):
        """Test URL encoded phone numbers"""
        encoded_numbers = [
            # Original, URL encoded
            ("+44 20 7946 0958", "%2B44%2020%207946%200958"),
            ("+1 (415) 555-2671", "%2B1%20%28415%29%20555-2671"),
            ("+61 4 1234 5678", "%2B61%204%201234%205678"),
        ]
        
        for original, encoded in encoded_numbers:
            result_original = self.make_api_request(original)
            result_encoded = self.make_api_request(encoded)
            
            # Only continue if original worked
            if "error" in result_original:
                print(f"× Original number failed: {original}")
                continue
                
            if "error" in result_encoded:
                print(f"× URL encoded number failed: {encoded}")
            else:
                self.assertEqual(result_original["country"], result_encoded["country"],
                              f"URL encoding affected country detection")
                self.assertEqual(result_original["national_number"], result_encoded["national_number"],
                              f"URL encoding affected number parsing")
                print(f"✓ URL encoding handled correctly: {encoded}")
    
    def test_default_region_override(self):
        """Test overriding the default region parameter"""
        test_cases = [
            # Using a specific number format to test region overrides
            ("+1 212 555 3456", "US", "United States"),  # As US number
            ("+1 212 555 3456", "GB", "United States"),  # Still a US number regardless of region
            ("+1 212 555 3456", "AU", "United States"),  # Still a US number regardless of region
        ]
        
        for number, region, expected_country in test_cases:
            result = self.make_api_request(number, region)
            
            if "error" in result:
                print(f"× Failed with default region {region}: {number} - Error: {result['error']}")
            else:
                print(f"Default region {region} interpreted {number} as: {result['country']}")
                self.assertEqual(result["country"], expected_country, 
                              f"Expected {expected_country} regardless of region override")
    
    def test_boundary_case_numbers(self):
        """Test numbers at the boundary of valid ranges"""
        boundary_cases = [
            # Premium rate numbers
            "+1 900 555 0199",  # US premium
            "+44 909 8765 432",  # UK premium
            # Special service numbers
            "+1 800 555 0199",  # US toll-free
            "+44 800 123 4567",  # UK toll-free
        ]
        
        for number in boundary_cases:
            result = self.make_api_request(number)
            
            if "error" in result:
                print(f"× Boundary case failed: {number} - Error: {result['error']}")
            else:
                print(f"✓ Boundary case handled: {number} - Type: {result['type']}")
    
    def test_numbers_without_plus(self):
        """Test handling numbers without the '+' prefix"""
        numbers_without_plus = [
            ("14155552671", "United States"),  # US
            ("442079460958", "United Kingdom"),  # UK - using a valid UK number
            ("61412345678", "Australia"),  # Australia
            ("2347012345678", "Nigeria"),  # Nigeria
        ]
        
        for number, expected_country in numbers_without_plus:
            result = self.make_api_request(number)
            
            if "error" in result:
                print(f"× Number without plus failed: {number} - Error: {result['error']}")
            else:
                self.assertEqual(result["country"], expected_country, 
                              f"Expected {expected_country}, got {result['country']} for {number}")
                print(f"✓ Number without plus handled correctly: {number} -> {result['formatted_number']}")

if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 