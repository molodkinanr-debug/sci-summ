from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base  # Измененный импорт

class PDFFile(Base):
    __tablename__ = "pdf_files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500))
    extracted_text = Column(Text)
    file_size = Column(Integer)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # user = relationship("User", back_populates="pdf_files")
    # predictions = relationship("PredictionHistory", back_populates="pdf_file")

class PredictionRequest(Base):
    __tablename__ = "prediction_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pdf_file_id = Column(Integer, ForeignKey("pdf_files.id"))
    input_text = Column(Text, nullable=False)
    status = Column(String(20), default="pending")
    cost = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # user = relationship("User", back_populates="prediction_requests")
    # pdf_file = relationship("PDFFile")

class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_id = Column(Integer, ForeignKey("prediction_requests.id"))
    pdf_file_id = Column(Integer, ForeignKey("pdf_files.id"))
    input_text = Column(Text)
    summary = Column(Text)
    model_used = Column(String(50))
    processing_time = Column(Float)
    cost = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # user = relationship("User", back_populates="prediction_history")
    # request = relationship("PredictionRequest")
    # pdf_file = relationship("PDFFile", back_populates="predictions")
