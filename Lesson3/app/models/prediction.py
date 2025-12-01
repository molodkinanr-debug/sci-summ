from datetime import datetime  
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.config import Base
from sqlalchemy import event as Event

class PDFFile(Base):
    __tablename__ = "pdf_files"
    __table_args__ = {'extend_existing': True}    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500))
    extracted_text = Column(Text)
    file_size = Column(Integer)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # user = relationship("User", back_populates="pdf_files")
    # predictions = relationship("PredictionHistory", back_populates="pdf_file")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("accounts.id"))
    
    # Входные данные
    text = Column(Text)
    model_type = Column(String)
    
    # Выходные данные
    summary = Column(Text)
    status = Column(String)  # 'pending', 'completed', 'failed'
    confidence_score = Column(Float, nullable=True)
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    @staticmethod
    def validate_text(text):
        if not text or len(text.strip()) < 10:
            raise ValueError("Invalid text length")
        return text.strip()
    
    @staticmethod
    def validate_model_type(model_type):
        if model_type not in ['t5', 'bart', 'pegasus']:
            raise ValueError("Invalid model type")
        return model_type

@Event.listens_for(Prediction, 'before_insert')
def validate_prediction_data(mapper, connection, target):
    target.text = Prediction.validate_text(target.text)
    target.model_type = Prediction.validate_model_type(target.model_type)