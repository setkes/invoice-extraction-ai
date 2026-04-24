import sys
import shutil
from pathlib import Path

# Adds the project root to sys.path so that "from app.xxx import ..."
# also works inside uvicorn subprocess workers (SpawnProcess)
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# load_dotenv() must be called BEFORE importing app.llm, because llm.py
# creates the OpenAI client at module level by reading OPENAI_API_KEY
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, UploadFile, File, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import select, Session, and_

from app.llm import extract_invoice_data
from app.database import get_session
from app.models import Document

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


def _fmt_amount(value):
    """Format a decimal as Swiss-style number: 4'000.00"""
    if value is None:
        return "-"
    try:
        return f"{float(value):,.2f}".replace(",", "'")
    except (ValueError, TypeError):
        return str(value)


templates.env.filters["chf"] = _fmt_amount

# Directory where uploaded PDFs are saved
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def home(request: Request, session: Session = Depends(get_session)):
    """
    Reads all invoices from the DB using SQLModel.

    Depends(get_session) is FastAPI's dependency injection:
    FastAPI automatically creates the DB session and passes it to the function.
    You don't need to open or close anything manually.

    select(Document) internally generates: SELECT * FROM documents
    .order_by() adds: ORDER BY created_at DESC
    session.exec(...).all() executes the query and returns a list of Document.
    """
    documents = session.exec(
        select(Document).order_by(Document.created_at.desc())
    ).all()

    return templates.TemplateResponse(
        request,
        "index.html",
        {"documents": documents},
    )


@app.post("/upload")
async def upload_invoice(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    """
    Receives the PDF, sends it to GPT, and saves the extracted data to the DB.

    Flow:
      1. Save the PDF to the uploads/ directory
      2. Send the PDF to GPT, which returns the fields as JSON
      3. Create a Document object with the extracted data
      4. session.add() + session.commit() persist to the DB (no raw SQL!)
      5. Redirect to the home page
    """

    # 1. Save the PDF to disk
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # 2. Ask GPT to extract invoice fields from the PDF
        data = extract_invoice_data(str(file_path))
        status = "processed"
    except Exception as e:
        data = {}
        status = "failed"
        print(f"Error while processing {file.filename}: {e}")

    # Duplicate detection: only meaningful when extraction succeeded.
    # If status is "failed", data is empty and all fields are None —
    # comparing NULL=NULL=NULL would flag every failed invoice as a duplicate.
    is_duplicate = False
    original_id = None
    if status == "processed":
        existing = session.exec(
            select(Document).where(
                and_(
                    Document.supplier_name == data.get("supplier_name"),
                    Document.invoice_number == data.get("invoice_number"),
                    Document.total_amount == data.get("total_amount"),
                )
            )
        ).first()
        is_duplicate = existing is not None
        original_id = existing.id if existing is not None else None

    # 3. Create a Document object — no raw SQL needed
    doc = Document(
        filename=file.filename,
        supplier_name=data.get("supplier_name"),
        customer_name=data.get("customer_name"),
        customer_address=data.get("customer_address"),
        description=data.get("description"),
        invoice_number=data.get("invoice_number"),
        invoice_date=data.get("invoice_date"),
        due_date=data.get("due_date"),
        currency=data.get("currency"),
        subtotal_amount=data.get("subtotal_amount"),
        vat_amount=data.get("vat_amount"),
        vat_rate=data.get("vat_rate"),
        discount_amount=data.get("discount_amount"),
        total_amount=data.get("total_amount"),
        notes=data.get("notes"),
        supplier_vat_number=data.get("supplier_vat_number"),
        payment_iban=data.get("payment_iban"),
        reference_number=data.get("reference_number"),
        status=status,
        confidence=data.get("confidence"),
        is_duplicate=is_duplicate,
        original_id=original_id,
    )

    # 4. Persist to DB: add() stages the record, commit() sends it
    session.add(doc)
    session.commit()

    # 5. Redirect to home
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{doc_id}")
def delete_invoice(
    doc_id: int,
    session: Session = Depends(get_session),
):
    """
    Deletes an invoice from the database by its ID.

    We use POST instead of DELETE because HTML forms only support
    GET and POST — not HTTP methods like DELETE.
    doc_id is read from the URL: /delete/5 deletes the invoice with id=5.
    """
    doc = session.get(Document, doc_id)  # look up by primary key
    if doc:
        session.delete(doc)
        session.commit()
    return RedirectResponse(url="/", status_code=303)
