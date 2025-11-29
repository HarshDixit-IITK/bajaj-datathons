"""Test script for the bill extraction API."""
import requests
import json
import sys


def test_extraction(document_url: str):
    """Test the extraction API with a document URL."""
    
    # API endpoint
    url = "http://localhost:8000/extract-bill-data"
    
    # Request payload
    payload = {
        "document": document_url
    }
    
    print(f"Testing API with document: {document_url}")
    print(f"Sending request to: {url}")
    print("-" * 80)
    
    try:
        # Send POST request
        response = requests.post(url, json=payload, timeout=120)
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            
            print("✓ Request successful!")
            print(f"Success: {data.get('is_success')}")
            print("-" * 80)
            
            if data.get('is_success'):
                extracted_data = data.get('data', {})
                
                print(f"Total Items: {extracted_data.get('total_item_count')}")
                print(f"Reconciled Amount: ${extracted_data.get('reconciled_amount')}")
                
                if extracted_data.get('actual_bill_total'):
                    print(f"Actual Bill Total: ${extracted_data.get('actual_bill_total')}")
                
                if extracted_data.get('accuracy_percentage'):
                    print(f"Accuracy: {extracted_data.get('accuracy_percentage')}%")
                
                print("-" * 80)
                print("\nLine Items by Page:")
                print("-" * 80)
                
                for page in extracted_data.get('pagewise_line_items', []):
                    print(f"\nPage {page.get('page_no')}:")
                    
                    for item in page.get('bill_items', []):
                        print(f"  • {item.get('item_name')}")
                        print(f"    Amount: ${item.get('item_amount')}")
                        if item.get('item_rate'):
                            print(f"    Rate: ${item.get('item_rate')}")
                        if item.get('item_quantity'):
                            print(f"    Quantity: {item.get('item_quantity')}")
                        print()
                    
                    if page.get('sub_total'):
                        print(f"  Sub-total: ${page.get('sub_total')}")
                        print()
                
                print("-" * 80)
                print("\nFull Response JSON:")
                print(json.dumps(data, indent=2))
            else:
                print(f"Error: {data.get('error')}")
        else:
            print(f"✗ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to the API. Make sure the server is running.")
        print("  Start the server with: python run.py")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    # Default test URL (from the problem statement)
    default_url = "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
    
    # Check if URL provided as argument
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = default_url
    
    test_extraction(test_url)

