import unittest
import sys
import time
import argparse
from typing import List

# Import test modules
from test_phone_numbers_comprehensive import TestPhoneNumbersComprehensive
from test_phone_numbers_advanced import TestPhoneNumbersAdvanced
from test_phone_numbers_edge_cases import TestPhoneNumbersEdgeCases

def run_test_suite(test_classes: List, test_name: str = None):
    """Run a suite of tests and print a summary"""
    start_time = time.time()
    
    # Create a test suite
    suite = unittest.TestSuite()
    
    if test_name:
        print(f"Running only test: {test_name}")
        
        # Add specific named test to suite
        for test_class in test_classes:
            try:
                suite.addTest(test_class(test_name))
            except ValueError:
                # Test not found in this class, that's ok
                continue
    else:
        # Add all tests from the specified classes
        for test_class in test_classes:
            # Use unittest.defaultTestLoader instead of makeSuite
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(test_class))
    
    # Run the tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Calculate and print summary
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print("\n" + "=" * 80)
    print(f"TESTS COMPLETED IN {elapsed_time:.2f} SECONDS")
    print(f"Total tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)
    
    # Print failures and errors for debugging
    if result.failures or result.errors:
        print("\nFAILURES AND ERRORS:\n")
        
        for test, error in result.failures:
            print(f"FAILURE: {test}")
            print(error)
            print("")
        
        for test, error in result.errors:
            print(f"ERROR: {test}")
            print(error)
            print("")
    
    # Return appropriate exit code
    if result.failures or result.errors:
        return 1
    else:
        return 0

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run phone number API tests")
    parser.add_argument("--test", help="Run a specific test by name")
    parser.add_argument("--class", dest="test_class", help="Run tests from a specific class only")
    args = parser.parse_args()
    
    # Classes to run
    test_classes = [
        TestPhoneNumbersComprehensive,
        TestPhoneNumbersAdvanced,
        TestPhoneNumbersEdgeCases
    ]
    
    # If a specific class was requested
    if args.test_class:
        class_mapping = {
            "comprehensive": TestPhoneNumbersComprehensive,
            "advanced": TestPhoneNumbersAdvanced,
            "edge": TestPhoneNumbersEdgeCases
        }
        
        if args.test_class.lower() in class_mapping:
            test_classes = [class_mapping[args.test_class.lower()]]
        else:
            print(f"Error: Unknown test class '{args.test_class}'")
            print(f"Available classes: {', '.join(class_mapping.keys())}")
            sys.exit(1)
    
    # Print header
    print("\n" + "=" * 80)
    print("RUNNING PHONE NUMBER API TESTS")
    print(f"Test classes: {', '.join([cls.__name__ for cls in test_classes])}")
    print("=" * 80 + "\n")
    
    # Run the tests
    exit_code = run_test_suite(test_classes, args.test)
    sys.exit(exit_code) 