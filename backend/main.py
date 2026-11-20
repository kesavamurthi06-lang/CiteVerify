
from services.evidence_retriever import retrieve_evidence
from services.evidence_verify import verify_claim

from fastapi import FastAPI, UploadFile, File, HTTPException

from services.citation_detector import detect_citations

from services.citation_matcher import match_citations

from services.paper_retriever import search_research_papers

from fastapi.middleware.cors import CORSMiddleware

import pymupdf
from docx import Document
from services.claim_extractor import extract_claims

from io import BytesIO

app = FastAPI(
    title="CiteVerify API",
    description="Scientific Claim and Citation Verification System",
    version="1.0.0"
)

# Allow React frontend to communicate with backend

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cite-verify-gamma.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 15 * 1024 * 1024


@app.get("/")
def home():
    return {
        "message": "Welcome to CiteVerify API",
        "status": "Backend running successfully"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# PDF TEXT EXTRACTION

def extract_pdf_text(content):

    pdf = pymupdf.open(
        stream=content,
        filetype="pdf"
    )

    text = ""

    page_count = len(pdf)

    for page in pdf:
        text += page.get_text() + "\n"

    pdf.close()

    return text, page_count


# DOCX TEXT EXTRACTION

def extract_docx_text(content):

    document = Document(BytesIO(content))

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    # Extract text from tables too

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                text += cell.text + "\n"

    return text, 0


# DOCUMENT UPLOAD API

@app.post("/api/documents/extract")
async def upload_document(file: UploadFile = File(...)):

    filename = file.filename or ""

    extension = filename.lower().split(".")[-1]

    if extension not in ["pdf", "docx"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must be less than 15 MB."
        )

    try:

        if extension == "pdf":

            if not content.startswith(b"%PDF-"):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid PDF file."
                )

            extracted_text, page_count = extract_pdf_text(content)

        else:

            if not content.startswith(b"PK"):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid DOCX file."
                )

            extracted_text, page_count = extract_docx_text(content)

        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No readable text found. The document may be scanned or image-based."
            )

        word_count = len(extracted_text.split())

        return {
            "success": True,
            "filename": filename,
            "file_type": extension,
            "page_count": page_count,
            "word_count": word_count,
            "extracted_text": extracted_text,
            "message": "Document processed successfully."
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Document processing failed: {str(error)}"
        )


# AI CLAIM EXTRACTION API

@app.post("/api/documents/extract-claims")
async def extract_document_claims(
    file: UploadFile = File(...)
):

    filename = file.filename or ""

    extension = filename.lower().split(".")[-1]

    if extension not in ["pdf", "docx"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    content = await file.read()

    if not content or len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Invalid or oversized document."
        )

    try:

        if extension == "pdf":

            if not content.startswith(b"%PDF-"):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid PDF file."
                )

            text, _ = extract_pdf_text(content)

        else:

            if not content.startswith(b"PK"):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid DOCX file."
                )

            text, _ = extract_docx_text(content)

        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="No readable text found."
            )

        claims = extract_claims(text)

        return {
            "success": True,
            "filename": filename,
            "total_claims": len(claims.get("claims", [])),
            "claims": claims.get("claims", [])
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"AI claim extraction failed: {str(error)}"
        )

@app.post("/api/citations/detect")
async def citation_detection(file: UploadFile = File(...)):

    filename = file.filename or ""

    content = await file.read()

    if not content or len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Invalid or oversized document."
        )

    try:

        if filename.lower().endswith(".pdf"):

            if not content.startswith(b"%PDF-"):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid PDF."
                )

            text, _ = extract_pdf_text(content)

        elif filename.lower().endswith(".docx"):

            if not content.startswith(b"PK"):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid DOCX."
                )

            text, _ = extract_docx_text(content)

        else:

            raise HTTPException(
                status_code=400,
                detail="Unsupported document format."
            )

        result = detect_citations(text)

        matches = match_citations(
            result["in_text_citations"],
            result["references"]
        )

        result["citation_matches"] = matches

        return {
            "success": True,
            "filename": filename,
            **result
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
@app.post("/api/claims/verify")
async def verify_scientific_claim(data: dict):

    claim = data.get("claim", "").strip()

    if not claim:
        raise HTTPException(
            status_code=400,
            detail="Scientific claim is required."
        )

    try:

        # Retrieve research evidence
        evidence = await retrieve_evidence(claim)

        # Verify claim against retrieved evidence
        result = verify_claim(claim, evidence)

        return {
            "claim": claim,
            "evidence_count": len(evidence),
            "evidence": evidence,
            "verification": result
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(error)}"
        )    

