#!/bin/bash

# Bill Data Extraction API - cURL Examples

API_URL="http://localhost:8000"

echo "=========================================="
echo "Bill Data Extraction API - cURL Examples"
echo "=========================================="
echo ""

# Example 1: Health Check
echo "1. Health Check"
echo "----------------"
curl -X GET "$API_URL/health" | jq '.'
echo ""
echo ""

# Example 2: Basic Extraction
echo "2. Basic Bill Extraction"
echo "------------------------"
curl -X POST "$API_URL/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
  }' | jq '.'
echo ""
echo ""

# Example 3: Extract with custom timeout
echo "3. Extraction with Timeout"
echo "--------------------------"
curl -X POST "$API_URL/extract-bill-data" \
  -H "Content-Type: application/json" \
  --max-time 120 \
  -d '{
    "document": "https://example.com/your-bill.png"
  }' | jq '.'
echo ""
echo ""

# Example 4: Pretty print specific fields
echo "4. Extract Specific Fields"
echo "--------------------------"
curl -X POST "$API_URL/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
  }' | jq '{
    success: .is_success,
    total_items: .data.total_item_count,
    total_amount: .data.reconciled_amount,
    accuracy: .data.accuracy_percentage
  }'
echo ""
echo ""

# Example 5: Save to file
echo "5. Save Results to File"
echo "-----------------------"
curl -X POST "$API_URL/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
  }' -o extraction_result.json
echo "✓ Results saved to extraction_result.json"
echo ""

echo "=========================================="
echo "Examples completed!"
echo "=========================================="

