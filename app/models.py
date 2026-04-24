from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import SQLModel, Field


class Document(SQLModel, table=True):
    """
    Represents the 'documents' table in the database.

    SQLModel, table=True  →  this is a real DB table
    Field(...)            →  describes the properties of each column
    Optional[str]         →  the field can be NULL in the DB

    No SQL needed: SQLModel automatically generates
    INSERT, SELECT, etc. queries from this class.
    """

    __tablename__ = "documents"  # exact table name in the DB

    # --- Identity ---
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    status: Optional[str] = "processed"
    confidence: Optional[Decimal] = None
    created_at: Optional[datetime] = None

    # --- Duplicate detection ---
    is_duplicate: Optional[bool] = False
    original_id: Optional[int] = None

    # --- Invoice metadata ---
    description: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None

    # --- Parties ---
    supplier_name: Optional[str] = None
    supplier_vat_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None

    # --- Amounts ---
    currency: Optional[str] = None
    subtotal_amount: Optional[Decimal] = None
    vat_rate: Optional[Decimal] = None        # percentage, e.g. 8.1
    vat_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None

    # --- Payment ---
    payment_iban: Optional[str] = None

    # --- Raw extraction data (for debugging) ---
    extracted_text: Optional[str] = None
    extracted_data_json: Optional[str] = None
