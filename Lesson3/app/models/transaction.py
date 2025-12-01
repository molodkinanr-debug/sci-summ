from datetime import datetime  
from app.database.config import Base  
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    amount = Column(Float)
    type = Column(String)  # 'credit', 'debit'
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)  
    account = relationship("app.models.account.Account", back_populates="transactions")
    
