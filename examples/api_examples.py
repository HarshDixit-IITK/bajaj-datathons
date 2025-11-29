"""
API Usage Examples

This file demonstrates various ways to use the Bill Data Extraction API.
"""

import requests
import json
from typing import Dict, Any


# Configuration
API_BASE_URL = "http://localhost:8000"


def example_basic_extraction():
    """Basic bill extraction example."""
    print("=" * 80)
    print("Example 1: Basic Bill Extraction")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/extract-bill-data"
    payload = {
        "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('is_success'):
            print("✓ Extraction successful!")
            print(f"\nTotal Items: {data['data']['total_item_count']}")
            print(f"Reconciled Amount: ${data['data']['reconciled_amount']}")
            
            if data['data'].get('accuracy_percentage'):
                print(f"Accuracy: {data['data']['accuracy_percentage']}%")
            
            print("\nLine Items:")
            for page in data['data']['pagewise_line_items']:
                print(f"\n  Page {page['page_no']}:")
                for item in page['bill_items']:
                    print(f"    • {item['item_name']}: ${item['item_amount']}")
        else:
            print(f"✗ Extraction failed: {data.get('error')}")
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
    
    print()


def example_batch_processing():
    """Process multiple bills."""
    print("=" * 80)
    print("Example 2: Batch Processing")
    print("=" * 80)
    
    bills = [
        "https://example.com/bill1.png",
        "https://example.com/bill2.png",
        "https://example.com/bill3.png"
    ]
    
    url = f"{API_BASE_URL}/extract-bill-data"
    results = []
    
    for i, bill_url in enumerate(bills, 1):
        print(f"\nProcessing bill {i}/{len(bills)}...")
        
        try:
            response = requests.post(url, json={"document": bill_url}, timeout=120)
            data = response.json()
            results.append({
                "url": bill_url,
                "success": data.get('is_success'),
                "data": data.get('data')
            })
            
            if data.get('is_success'):
                print(f"  ✓ Success: {data['data']['total_item_count']} items, ${data['data']['reconciled_amount']}")
            else:
                print(f"  ✗ Failed: {data.get('error')}")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                "url": bill_url,
                "success": False,
                "error": str(e)
            })
    
    print(f"\n\nSummary: {sum(1 for r in results if r['success'])}/{len(bills)} successful")
    print()


def example_error_handling():
    """Demonstrate error handling."""
    print("=" * 80)
    print("Example 3: Error Handling")
    print("=" * 80)
    
    # Test with invalid URL
    url = f"{API_BASE_URL}/extract-bill-data"
    payload = {
        "document": "https://invalid-url.com/nonexistent.png"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        data = response.json()
        
        if data.get('is_success'):
            print("✓ Extraction successful")
        else:
            print(f"✗ Extraction failed: {data.get('error')}")
    
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
    except requests.exceptions.ConnectionError:
        print("✗ Connection error - is the API running?")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    print()


def example_detailed_analysis():
    """Detailed analysis of extraction results."""
    print("=" * 80)
    print("Example 4: Detailed Analysis")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/extract-bill-data"
    payload = {
        "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        data = response.json()
        
        if data.get('is_success'):
            extracted = data['data']
            
            print(f"Document Analysis:")
            print(f"  Total Pages: {len(extracted['pagewise_line_items'])}")
            print(f"  Total Items: {extracted['total_item_count']}")
            print(f"  Reconciled Amount: ${extracted['reconciled_amount']}")
            
            if extracted.get('actual_bill_total'):
                print(f"  Actual Bill Total: ${extracted['actual_bill_total']}")
                difference = abs(extracted['reconciled_amount'] - extracted['actual_bill_total'])
                print(f"  Difference: ${difference:.2f}")
            
            if extracted.get('accuracy_percentage'):
                print(f"  Accuracy: {extracted['accuracy_percentage']}%")
            
            # Item statistics
            all_items = []
            for page in extracted['pagewise_line_items']:
                all_items.extend(page['bill_items'])
            
            amounts = [item['item_amount'] for item in all_items]
            print(f"\nItem Statistics:")
            print(f"  Average Amount: ${sum(amounts) / len(amounts):.2f}")
            print(f"  Min Amount: ${min(amounts):.2f}")
            print(f"  Max Amount: ${max(amounts):.2f}")
            
            # Items with missing data
            missing_rate = sum(1 for item in all_items if item.get('item_rate') is None)
            missing_qty = sum(1 for item in all_items if item.get('item_quantity') is None)
            
            if missing_rate or missing_qty:
                print(f"\nData Completeness:")
                if missing_rate:
                    print(f"  Items missing rate: {missing_rate}")
                if missing_qty:
                    print(f"  Items missing quantity: {missing_qty}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_health_check():
    """Check API health."""
    print("=" * 80)
    print("Example 5: Health Check")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/health"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        print("API Health Status:")
        print(f"  Status: {data.get('status')}")
        print(f"  OCR Engine: {data.get('ocr_engine')}")
        print(f"  GPT Model: {data.get('gpt_model')}")
        print(f"  OpenAI Configured: {data.get('openai_configured')}")
    
    except Exception as e:
        print(f"✗ Health check failed: {e}")
    
    print()


def example_save_to_file():
    """Extract and save results to file."""
    print("=" * 80)
    print("Example 6: Save Results to File")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/extract-bill-data"
    payload = {
        "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        data = response.json()
        
        if data.get('is_success'):
            # Save to JSON file
            output_file = "extraction_result.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✓ Results saved to {output_file}")
            
            # Also save a CSV summary
            import csv
            csv_file = "extraction_summary.csv"
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Page', 'Item Name', 'Quantity', 'Rate', 'Amount'])
                
                for page in data['data']['pagewise_line_items']:
                    for item in page['bill_items']:
                        writer.writerow([
                            page['page_no'],
                            item['item_name'],
                            item.get('item_quantity', 'N/A'),
                            item.get('item_rate', 'N/A'),
                            item['item_amount']
                        ])
            
            print(f"✓ Summary saved to {csv_file}")
        else:
            print(f"✗ Extraction failed: {data.get('error')}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("Bill Data Extraction API - Usage Examples")
    print("=" * 80)
    print()
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ API is running\n")
        else:
            print("✗ API returned unexpected status\n")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Please start the server with: python run.py\n")
        return
    
    # Run examples
    example_basic_extraction()
    example_health_check()
    example_detailed_analysis()
    # example_batch_processing()  # Uncomment for batch processing
    # example_error_handling()    # Uncomment for error handling demo
    # example_save_to_file()      # Uncomment to save results
    
    print("=" * 80)
    print("Examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()

