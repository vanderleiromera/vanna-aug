#!/usr/bin/env python3
"""
Simple script to test array conditions.
"""

class ArrayTest:
    def test_condition(self, array):
        """Test different ways of checking array conditions."""
        print(f"Testing array: {array}")
        
        # Test different conditions
        try:
            if array:
                print("Direct condition check: True")
            else:
                print("Direct condition check: False")
        except Exception as e:
            print(f"Direct condition check error: {e}")
        
        try:
            if array is not None:
                print("is not None check: True")
            else:
                print("is not None check: False")
        except Exception as e:
            print(f"is not None check error: {e}")

def main():
    """Main function."""
    tester = ArrayTest()
    
    # Test with a list
    tester.test_condition([1, 2, 3, 4, 5])
    
    # Test with None
    tester.test_condition(None)
    
    # Create a simple array-like object that will raise an error
    class ArrayLike:
        def __bool__(self):
            raise ValueError("The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()")
    
    # Test with the array-like object
    tester.test_condition(ArrayLike())

if __name__ == "__main__":
    main()
