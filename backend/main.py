import os
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import ChatRequest, ChatResponse
from services.embedding_service import create_embedding
from services.pinecone_service import search_pinecone
from services.llm_service import generate_answer
from services.document_service import extract_text
from services.summarization_service import summarize_text


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "RAG Chatbot API is running"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    embedding = create_embedding(
        request.question
    )

    context = search_pinecone(
        embedding
    )

    answer = generate_answer(
        request.question,
        context
    )

    return ChatResponse(
        answer=answer
    )


@app.post("/summarize")
async def summarize_file(
    file: UploadFile = File(...)
):

    allowed_extensions = [
        ".pdf",
        ".docx",
        ".txt"
    ]

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX, and TXT files are supported."
        )

    try:

        # Read uploaded file
        file_content = await file.read()

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_file.write(file_content)
            temp_path = temp_file.name

        # Extract text
        text = extract_text(
            temp_path,
            file.filename
        )

        # Delete temporary file
        os.remove(temp_path)

        if not text.strip():

            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the file."
            )

        # Summarize extracted text
        summary = summarize_text(text)

        return {
            "filename": file.filename,
            "summary": summary
        }

    except HTTPException:
        raise

    except Exception as error:

        print("ERROR:", error)

        raise HTTPException(
            status_code=500,
            detail="Failed to process the document."
        )