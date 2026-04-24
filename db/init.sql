-- Creates the documents table if it does not already exist.
-- Each row represents one processed invoice.
CREATE TABLE IF NOT EXISTS documents (
    id                  SERIAL PRIMARY KEY,
    filename            TEXT NOT NULL,
    supplier_name       TEXT,
    customer_name       TEXT,
    customer_address    TEXT,
    invoice_number      TEXT,
    invoice_date        DATE,
    due_date            DATE,
    currency            TEXT,
    subtotal_amount     NUMERIC(12, 2),
    vat_amount          NUMERIC(12, 2),
    vat_rate            NUMERIC(5, 2),
    discount_amount     NUMERIC(12, 2),
    total_amount        NUMERIC(12, 2),
    description         TEXT,
    notes               TEXT,
    supplier_vat_number TEXT,
    payment_iban        TEXT,
    reference_number    TEXT,
    status              TEXT DEFAULT 'processed',
    confidence          NUMERIC(4, 3),
    is_duplicate        BOOLEAN DEFAULT FALSE,
    original_id         INTEGER,
    extracted_text      TEXT,
    extracted_data_json TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- Grant access to the application user
GRANT ALL ON SCHEMA public TO invoice_user;
GRANT ALL PRIVILEGES ON TABLE documents TO invoice_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO invoice_user;