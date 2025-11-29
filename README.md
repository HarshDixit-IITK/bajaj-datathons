# Bill Data Extraction API

An intelligent bill/invoice data extraction system that uses OCR and Large Language Models (LLMs) to extract line items, amounts, and totals from bill images with high accuracy.

## 🎯 Overview

This project provides a REST API that:
- Extracts line item details from multi-page bills and invoices
- Provides individual line item amounts, sub-totals, and final totals
- Ensures no line items are missed or double-counted
- Reconciles extracted amounts with actual bill totals
- Calculates extraction accuracy

## 🏗️ Architecture

The system uses a multi-stage pipeline:

1. **Document Processing**: Downloads and preprocesses bill images
2. **OCR Extraction**: Extracts text using EasyOCR or Tesseract
3. **Intelligent Extraction**: Uses GPT-4 Vision to identify and extract line items
4. **Reconciliation**: Validates and reconciles amounts without double-counting
5. **Accuracy Calculation**: Compares extracted totals with actual bill totals

### Technology Stack

- **FastAPI**: High-performance web framework for the API
- **EasyOCR**: Accurate OCR engine for text extraction
- **Pydantic**: Data validation and serialization
- **OpenCV & Pillow**: Image processing and enhancement

## 📋 Features

✅ Multi-page bill support  
✅ Intelligent line item detection  
✅ Handles various bill formats and layouts  
✅ Extracts item name, quantity, rate, and amount  
✅ Identifies sub-totals where they exist  
✅ Prevents double-counting  
✅ Calculates extraction accuracy  
✅ Comprehensive error handling  
✅ Docker support for easy deployment  

## 🚀 Quick Start

### Prerequisites

- Python 3.11+

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd project
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

5. **Run the API**
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## 📡 API Usage

### Endpoint

```
POST /extract-bill-data
Content-Type: application/json
```

### Request Format

```json
{
  "document": "https://example.com/bill.png"
}
```

### Response Format

```json
{
  "is_success": true,
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "1",
        "bill_items": [
          {
            "item_name": "Livi 300mg Tab",
            "item_amount": 448.0,
            "item_rate": 32.0,
            "item_quantity": 14.0
          },
          {
            "item_name": "Metnuro",
            "item_amount": 124.03,
            "item_rate": 17.72,
            "item_quantity": 7.0
          }
        ],
        "sub_total": null
      }
    ],
    "total_item_count": 2,
    "reconciled_amount": 572.03,
    "actual_bill_total": 572.03,
    "accuracy_percentage": 100.0
  }
}
```

### Example Usage

**Python**
```python
import requests

url = "http://localhost:8000/extract-bill-data"
payload = {
    "document": "https://example.com/bill.png"
}

response = requests.post(url, json=payload)
data = response.json()

if data['is_success']:
    print(f"Total Items: {data['data']['total_item_count']}")
    print(f"Amount: ${data['data']['reconciled_amount']}")
    print(f"Accuracy: {data['data']['accuracy_percentage']}%")
```

**cURL**
```bash
curl -X POST "http://localhost:8000/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{"document": "https://example.com/bill.png"}'
```

**JavaScript/Node.js**
```javascript
const response = await fetch('http://localhost:8000/extract-bill-data', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    document: 'https://example.com/bill.png'
  })
});

const data = await response.json();
console.log(data);
```

## 🧪 Testing

A test script is provided to test the API with sample bills:

```bash
# Test with default sample bill
python test_api.py

# Test with custom URL
python test_api.py "https://example.com/your-bill.png"
```

## 📊 Accuracy & Reconciliation

The system ensures high accuracy through:

1. **Multi-stage Extraction**: Combines OCR and vision-based LLM extraction
2. **Smart Reconciliation**: Sums only line items, excludes sub-totals and taxes already included
3. **Validation**: Cross-references with actual bill totals
4. **Accuracy Metrics**: Calculates percentage accuracy of extraction

**Reconciliation Formula:**
```
Reconciled Amount = Sum of all individual line item amounts
Accuracy = 100 × (1 - |Reconciled Amount - Actual Bill Total| / Actual Bill Total)
```

## 🔧 Configuration

Configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port number | `8000` |
| `OCR_ENGINE` | OCR engine (`easyocr` or `tesseract`) | `easyocr` |

## 📁 Project Structure

```
project/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration management
│   ├── models.py             # Pydantic data models
│   ├── ocr_service.py        # OCR processing service
│   ├── extraction_service.py # LLM extraction service
│   └── main.py               # FastAPI application
├── requirements.txt          # Python dependencies
├── run.py                    # Application runner
├── test_api.py              # API test script
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── env.example              # Environment variables template
└── README.md               # This file
```

## 🎨 Key Features Explained

### 1. OCR Processing
- Uses EasyOCR for robust text extraction
- Image preprocessing for better OCR accuracy
- Handles various image formats and qualities

### 2. Intelligent Extraction
- Identifies line items even in complex layouts
- Handles items spanning multiple lines
- Recognizes discounts, taxes, and special cases

### 3. Reconciliation
- Prevents double-counting of sub-totals
- Validates against actual bill totals
- Provides accuracy metrics
- Handles edge cases (missing quantities, rates, etc.)

### 4. Error Handling
- Graceful fallback to text-only extraction
- Comprehensive logging
- Detailed error messages
- Validation at every step

## 🔍 How It Works

1. **Download Image**: Fetches bill image from provided URL
2. **OCR Extraction**: Extracts text using EasyOCR
3. **Vision Analysis**: Gemini Vision analyzes image + OCR text
4. **Line Item Extraction**: Identifies all line items with details
5. **Data Structuring**: Organizes data by pages
6. **Reconciliation**: Calculates totals without double-counting
7. **Validation**: Compares with actual bill total
8. **Response**: Returns structured JSON with accuracy metrics

## 🌟 Advantages

- **High Accuracy**: Combines OCR with vision-enabled LLMs
- **Flexible**: Handles various bill formats and layouts
- **Robust**: Multiple fallback mechanisms
- **Fast**: Optimized processing pipeline
- **Scalable**: Stateless API design
- **Easy to Deploy**: Docker support included

## 🛠️ Advanced Usage

### Custom OCR Engine

To use Tesseract instead of EasyOCR:

```bash
# Install Tesseract
# Ubuntu/Debian: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract

# Update .env
OCR_ENGINE=tesseract
```

### Batch Processing

For processing multiple bills:

```python
import requests

bills = [
    "https://example.com/bill1.png",
    "https://example.com/bill2.png",
    "https://example.com/bill3.png"
]

for bill_url in bills:
    response = requests.post(
        "http://localhost:8000/extract-bill-data",
        json={"document": bill_url}
    )
    print(response.json())
```

## 📝 API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🐛 Troubleshooting

### Common Issues

**1. "OpenAI client not initialized"**
- Ensure `gemini_api_key` is set in `.env`
- Verify the API key is valid

**2. "Failed to process document"**
- Check if the document URL is accessible
- Verify the image format is supported
- Ensure network connectivity

**3. "Import errors"**
- Reinstall dependencies: `pip install -r requirements.txt`
- Ensure you're using Python 3.11+

**4. OCR not working**
- For EasyOCR: Ensure sufficient memory (2GB+ recommended)
- For Tesseract: Verify installation with `tesseract --version`

## 📈 Performance Tips

- Use high-quality bill images (300 DPI or higher)
- Ensure good contrast in bill images
- For large batches, consider rate limiting
- Monitor OpenAI API usage and costs

## 🔐 Security Considerations

- Never commit `.env` file with API keys
- Use environment variables for sensitive data
- Implement rate limiting for production use
- Add authentication for public deployments

## 📦 Deployment

### Production Deployment

1. **Set environment variables** properly
2. **Use process manager** like systemd or PM2
3. **Set up reverse proxy** (nginx/Apache)
4. **Enable HTTPS** with SSL certificates
5. **Add monitoring** and logging
6. **Implement rate limiting**

### Cloud Deployment

The API can be deployed to:
- AWS (EC2, ECS, Lambda)
- Google Cloud (Cloud Run, Compute Engine)
- Azure (App Service, Container Instances)
- Heroku, Railway, Render

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Support for PDF bills
- Batch processing endpoints
- Additional OCR engines
- Multi-language support
- Cost optimization

## 📄 License

This project is provided as-is for the HackRx datathon.

## 👥 Author

Harsh dixit IITK



