# Invoice Extraction AI

A FastAPI web app that extracts structured data from PDF invoices using GPT and stores it in PostgreSQL.

Upload a PDF → GPT reads it → data saved to DB → displayed in a table.

---

## Features

- Upload PDF invoices via browser
- GPT extracts: supplier, customer, amounts, dates, VAT, IBAN, and more
- Duplicate detection (same supplier + invoice number + amount)
- Swiss number formatting (`4'320.50`)
- Per-row delete
- Confidence score per extraction

---

## Tech stack

| | |
|---|---|
| **FastAPI** | Web framework |
| **OpenAI GPT** | Invoice data extraction via Files API |
| **PostgreSQL** | Storage |
| **SQLModel** | ORM |
| **Jinja2** | HTML templates |

---

## Requirements

- Python 3.10+
- PostgreSQL
- An OpenAI API key

---

## Setup

```bash
# 1. Clone and create virtual environment
git clone https://github.com/your-username/invoice-extraction-ai.git
cd invoice-extraction-ai
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env and fill in your OpenAI API key and DB credentials

# 4. Set up the database (first time only)
sudo -u postgres bash setup.sh

# 5. Start the server
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** in your browser.

---

## Environment variables

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-proj-...
POSTGRES_DB=invoice_db
POSTGRES_USER=invoice_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
```

---

## Project structure

```
app/
├── main.py          # Routes and upload logic
├── llm.py           # GPT integration (OpenAI Files API)
├── models.py        # Database table definition
├── database.py      # DB engine and session factory
└── templates/
    └── index.html   # Browser UI
db/
└── init.sql         # Table creation script
setup.sh             # First-time DB setup
requirements.txt
```
