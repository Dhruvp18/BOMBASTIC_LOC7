from flask import Flask, request, jsonify
import requests
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

VERYFI_URL = "https://api.veryfi.com/api/v8/partner/documents"
HEADERS = {
    'Accept': 'application/json',
    'CLIENT-ID': 'vrfUf0oDw8PB7nVgBPfh0WUzmLHOiNE1pbn5pgf',
    'AUTHORIZATION': 'apikey pseudocause30:6ef1bd869175c48ca0461148218df858'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_receipt_data(json_data):
    vendor_info = {
        "name": json_data["vendor"].get("name") if json_data["vendor"].get("name") is not None else 0,
        "category": json_data["vendor"].get("category") if json_data["vendor"].get("category") is not None else 0,
        "registration_number": json_data["vendor"].get("reg_number") if json_data["vendor"].get("reg_number") is not None else 0
    }
    
    bill_info = {
        "date": json_data.get("date") if json_data.get("date") is not None else 0,
        "invoice_number": json_data.get("invoice_number") if json_data.get("invoice_number") is not None else 0,
        "currency": json_data.get("currency_code") if json_data.get("currency_code") is not None else 0,
        "payment_mode": json_data["payment"].get("display_name") if json_data["payment"].get("display_name") is not None else 0,
        "totalAmount": json_data.get("total") if json_data.get("total") is not None else 0,
        "totalTax": json_data.get("tax") if json_data.get("tax") is not None else 0
    }
    
    items = []
    for item in json_data.get("line_items", []):
        if item.get("type") == "discount":
            continue
            
        item_info = {
            "name": item.get("description") if item.get("description") is not None else 0,
            "quantity": item.get("quantity") if item.get("quantity") is not None else 0,
            "rate": item.get("price") if item.get("price") is not None else 0,
            "tax": item.get("tax") if item.get("tax") is not None else 0,
            "discount": item.get("discount") if item.get("discount") is not None else 0,
            "total": item.get("total") if item.get("total") is not None else 0
        }
        items.append(item_info)
    
    receipt_data = {
        "vendor": vendor_info,
        "bill": bill_info,
        "items": items,
        "total_items": len(items)
    }
    
    return receipt_data

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed: {file.filename}'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"Uploaded file: {filename}, Path: {filepath}, Size: {os.path.getsize(filepath)} bytes")
        
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filepath)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        print(f"MIME Type: {mime_type}")
        
        with open(filepath, 'rb') as image_file:
            files = {
                'file': (filename, image_file, mime_type)
            }
            
            # print(f"Headers: {HEADERS}")
            
            response = requests.post(VERYFI_URL, headers=HEADERS, files=files)
        
        os.remove(filepath)
        
        json_data = json.loads(response.text)
        receipt_data = extract_receipt_data(json_data)
        
        if response.status_code not in [200, 201]:
            print(f"Veryfi API Error: {response.status_code}, Response: {response.text}")
            return jsonify({'error': 'OCR service error', 'details': response.text}), 500
        
        
        return jsonify(receipt_data)
    
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        print(f"Exception occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
app.run(debug=True)