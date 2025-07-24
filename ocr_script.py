from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image, ImageEnhance, ImageFilter
import torch
import re

#Set device (GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#Load the processor and model
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed", use_fast = True)
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed").to(device)

def preprocess_image(image_path):
    image = Image.open(image_path).convert("L")
    image = image.filter(ImageFilter.MedianFilter(size=3))
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image = image.convert("RGB")
    return image

def run_trocr_ocr(image_path: str) -> str:
    """
    Function that takes a path to the image
    Returns the extracted text using TrOCR

    1. Image is converted to RGB format to ensure 3-channel color input regardless of the image format
    2. Passed through the preprocessor to resize and normalize and convert to pytorch tensor
    3. Generates a sequence of token IDs
    4. Convert the token IDs back into readable text
    """
    image = preprocess_image(image_path)
    pixel_values = processor(images = image, return_tensors="pt").pixel_values.to(device)
    generate_ids = model.generate(pixel_values, max_length=256)
    extracted_text = processor.batch_decode(generate_ids, skip_special_tokens=True)[0]
    return extracted_text

def extract_invoice_fields_from_text(text:str) -> dict:
    """
    Exracts structured invoice fields from raw OCR text.
    """
    fields = {}
    lines = text.strip().split('\n')
    fields["vendor"] = lines[0] if lines else ""

    match = re.search(r'Invoice\s*(No\.?|Number)?[:\s]*([A-Z0-9\-]+)', text, re.IGNORECASE)
    fields["invoice_number"] = match.group(2) if match else ""

    date_match = re.search(r'Date[:\s]*([\d]{1,2}[/-][\d]{1,2}[/-][\d]{2,4})', text, re.IGNORECASE)
    fields["date"] = date_match.group(1) if date_match else ""

    total_match = re.search(r'(Total Amount|Amount Due|Total)[:\s]*\$?([\d,]+\.\d{2})', text, re.IGNORECASE)
    fields["total"] = total_match.group(2) if total_match else ""

    return fields

if __name__ == "__main__":
    img_path = "excel-invoice-template-1x.png" 
    raw_text = run_trocr_ocr(img_path)
    print("\n Extracted Text:", raw_text)

    structured = extract_invoice_fields_from_text(raw_text)
    print("\n Extracted Invoice Fields:")
    for k,v in structured.items():
        print(f"{k.title()} : {v}")
    

