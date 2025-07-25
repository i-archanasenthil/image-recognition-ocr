import easyocr
import re

reader = easyocr.Reader(['en'])

def extract_invoice_data_from_image(image_path: str) -> dict:
    result = reader.readtext(image_path)
    raw_text = ' '.join([text for _, text, _ in result])

    return extract_invoice_data(raw_text)

def extract_invoice_data(text: str) -> dict:
    fields = {}

    text = text.replace('\n', ' ').replace('\r','').strip()

    vendor_match = re.search(r'^(.*?)\bINVOICE\b', text, re.IGNORECASE)
    if vendor_match:
        vendor = vendor_match.group(1).strip()
        fields['vendor'] = vendor
    else:
        fields['vendor'] = 'Unknown Vendor'
    
    match = re.findall(r'(INV[-\s]?[A-Z0-9]{3,})', text, re.IGNORECASE)
    for i, mat in enumerate(match, 1):
        print(f"{i} : {mat}")
    if len(match) >= 2:
        fields["invoice_number"] = match[2]
    elif match:
        fields["invoice_number"] = match[0]
    else:
        fields["invoice_number"] = 'Not found' 

    match = re.search( r'(\d{1,2})[\s/-]?(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[\s/-]?(\d{4})', text, re.IGNORECASE)
    if match:
        fields["date"] = f"{match.group(1)}/{match.group(2)}/{match.group(3)}" 

    match = re.findall(r'total\s*\$?([sS]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text, re.IGNORECASE)
    for i, mat in enumerate(match, 1):
        print(f"{i} : {mat}")
    
    if len(match) >= 2:
        fields["total"] = match[1]
    elif match:
        fields["total"] = match[0]
    else:
        fields["total"] = 'Not found' 


    return fields


invoice_info = extract_invoice_data_from_image('excel-invoice-template-1x.png')
print("\nExtracted text from the invoice")
for key, value in invoice_info.items():
    print(f"{key} : {value}")