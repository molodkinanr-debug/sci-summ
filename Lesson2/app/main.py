from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg2
from typing import Optional

app = FastAPI(
    title="Sci-Summ API", 
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

class SummarizationRequest(BaseModel):
    text: str
    max_length: Optional[int] = 200

class SummarizationResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int

def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

@app.get("/")
async def root():
    return {"message": "Sci-Summ API is running", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    """Проверка здоровья всех компонентов системы"""
    status = {"status": "healthy"}
    
    try:
        conn = get_db_connection()
        conn.close()
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        status["status"] = "unhealthy"
    
    return status

@app.post("/api/summarize", response_model=SummarizationResponse)
async def summarize_text(request: SummarizationRequest):
    """Эндпоинт для суммаризации текста"""
    try:
        # Простая логика суммаризации
        sentences = request.text.split('.')
        summary = '. '.join(sentences[:2]) + '.' if len(sentences) > 2 else request.text
        
        # Сохранение в базу данных
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO summarization_history (original_text, summary_text, original_length, summary_length)
            VALUES (%s, %s, %s, %s)
        """, (request.text, summary, len(request.text), len(summary)))
        conn.commit()
        cursor.close()
        conn.close()
        
        return SummarizationResponse(
            summary=summary,
            original_length=len(request.text),
            summary_length=len(summary)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/history")
async def get_summarization_history():
    """Получение истории суммаризаций"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, original_text, summary_text, original_length, summary_length, created_at
            FROM summarization_history
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                "id": row[0],
                "original_text": row[1][:100] + "..." if len(row[1]) > 100 else row[1],
                "summary_text": row[2],
                "original_length": row[3],
                "summary_length": row[4],
                "created_at": row[5].isoformat()
            })
        
        return {"history": history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Инициализация базы данных при запуске
@app.on_event("startup")
async def startup_event():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS summarization_history (
                id SERIAL PRIMARY KEY,
                original_text TEXT NOT NULL,
                summary_text TEXT NOT NULL,
                original_length INTEGER NOT NULL,
                summary_length INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv('API_HOST', '0.0.0.0'), 
        port=int(os.getenv('API_PORT', 8000))
    )
    
