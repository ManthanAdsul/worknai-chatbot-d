from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import StatusResponse
from app.services.rag_service import rag_service
from pypdf import PdfReader
import io

router = APIRouter()

@router.post("/admin/upload-pdf", response_model=StatusResponse)
async def upload_pdf(file: UploadFile = File(...)):
    try:
        pdf_content = await file.read()
        pdf_file = io.BytesIO(pdf_content)

        reader = PdfReader(pdf_file)
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        rag_service.add_documents(
            texts=[text],
            metadatas=[{"source": file.filename, "type": "pdf"}]
        )

        return StatusResponse(
            status="success",
            message=f"PDF '{file.filename}' uploaded and indexed successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/add-text", response_model=StatusResponse)
async def add_text(text: str, source: str = "manual"):
    try:
        rag_service.add_documents(
            texts=[text],
            metadatas=[{"source": source, "type": "text"}]
        )

        return StatusResponse(
            status="success",
            message="Text added to knowledge base successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
