from openai import OpenAI
import os
import json
from dotenv import load_dotenv

# Load .env before reading OPENAI_API_KEY.
# Necessary because in uvicorn subprocess workers the .env
# is not automatically inherited from the parent process.
load_dotenv()

# The OpenAI client reads the API key from the OPENAI_API_KEY environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Change the model here at any time
MODEL = "gpt-5.4-mini-2026-03-17"


def extract_invoice_data(pdf_path: str) -> dict:
    """
    Sends the PDF directly to GPT without converting it to text first.

    Step 1 — client.files.create():
        Uploads the file to OpenAI. OpenAI stores it temporarily
        and returns a 'file_id' (e.g. "file-abc123").
        purpose="user_data" indicates the file is input for a chat.

    Step 2 — client.chat.completions.create():
        The user message contains two "parts":
          - type "file": the just-uploaded PDF, identified by file_id
          - type "text": our question/instruction
        GPT reads the PDF directly (text, tables, layout) and responds.

    Step 3 — client.files.delete():
        Deletes the file from OpenAI after use to avoid leaving data around.

    response_format={"type": "json_object"} forces GPT to respond
    ONLY with valid JSON, so no complex parsing is needed.
    temperature=0 makes responses deterministic (less "creative").
    """
    prompt = """You are an expert at extracting structured data from Swiss invoices, often written in Italian (Ticino region).
Read the attached PDF and extract the following fields.
Respond ONLY with a valid JSON object with exactly these keys:

{
  "supplier_name": "name of the supplier",
  "customer_name": "name of the customer",
  "customer_address": "full customer address (street, postal code, city)",
  "description": "generic description of what the invoice is for (e.g. 'IT consulting services', 'Bathroom renovation work', 'Electrical materials supply')",
  "invoice_number": "invoice number",
  "invoice_date": "YYYY-MM-DD or null",
  "due_date": "YYYY-MM-DD or null",
  "currency": "CHF or EUR or USD etc.",
  "subtotal_amount": 0.00,
  "vat_amount": 0.00,
  "vat_rate": 8.1,
  "discount_amount": 0.00,
  "total_amount": 0.00,
  "notes": "any important notes found in the invoice (e.g. payment reason, warnings, special instructions) or null",
  "supplier_vat_number": "supplier VAT number",
  "payment_iban": "IBAN for payment",
  "reference_number": "reference number",
  "confidence": 0.95
}

Rules:
- If a field is not found in the PDF, use null.
- For amounts use numbers only (no currency symbols).
- vat_rate is the VAT percentage (e.g. 8.1, not 0.081). If not found, null.
- discount_amount is the discount amount if present, otherwise null.
- confidence ranges from 0.0 to 1.0 and reflects how certain you are about the extraction.
- description must be short (max 10 words), generic — do NOT list individual line items.
- notes: only if there are relevant notes, otherwise null.
"""

    # Step 1: upload the PDF to OpenAI
    with open(pdf_path, "rb") as f:
        uploaded = client.files.create(file=f, purpose="user_data")

    try:
        # Step 2: send the PDF to GPT as message content
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        # This part tells GPT: "read this PDF"
                        {"type": "file", "file": {"file_id": uploaded.id}},
                        # This part is our question/instruction
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
    finally:
        # Step 3: delete the file from OpenAI in all cases (even on error)
        client.files.delete(uploaded.id)

    # response.choices[0].message.content is the JSON string returned by GPT
    result = json.loads(response.choices[0].message.content)
    return result
