import hashlib
import time
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Импорты из наших модулей
from app.database.config import get_db
from app.models.user import User
from app.models.account import Account
from app.services.crud.user import create_user, authenticate_user, get_all_users
from app.services.crud.account import withdraw_from_account
from app.services.auth import create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES

# Временные схемы (вынесем позже)
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class AccountBalance(BaseModel):
    balance: float
    credit_limit: float

class PredictionRequest(BaseModel):
    text: str
    model_type: Optional[str] = "default"

class PredictionResponse(BaseModel):
    id: int
    user_id: int
    input_text: str
    summary: str
    model_used: str
    cost: float
    processing_time: float
    created_at: datetime

# Простая функция хэширования
def get_password_hash(password: str) -> str:
    salt = "sci_summ_salt"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

# Функция суммаризации (заглушка)
def summarize_text(text: str, model_type: str = "default") -> str:
    time.sleep(1)  # Имитация обработки
    if len(text) < 100:
        return text[:50] + "..."
    sentences = text.split('.')
    if len(sentences) > 3:
        summary = '. '.join(sentences[:3]) + '.'
    else:
        summary = text[:150] + "..."
    return summary

# Создаем приложение FastAPI
app = FastAPI(
    title="Sci-Summ API",
    description="REST API for Scientific Articles Summarization System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Эндпоинты
@app.post("/auth/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_data.dict())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    return user

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/accounts/balance", response_model=AccountBalance)
def get_balance(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {
        "balance": account.balance,
        "credit_limit": account.credit_limit
    }

@app.post("/accounts/deposit")
def deposit(
    amount: float,
    description: str = "Deposit",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    if not account:
        account = Account(user_id=current_user.id, balance=0.0)
        db.add(account)
    
    account.balance += amount
    db.commit()
    
    return {"message": f"Successfully deposited {amount}", "new_balance": account.balance}

@app.post("/predictions/summarize", response_model=PredictionResponse)
def create_prediction(
    prediction_data: PredictionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Проверяем баланс
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=400, detail="Account not found")
    
    cost = 1.0
    if account.balance < cost:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient balance. Required: {cost}, Available: {account.balance}"
        )
    
    # Используем withdraw_from_account вместо прямого списания
    try:
        withdraw_from_account(db, account.id, cost, f"Payment for prediction: {prediction_data.model_type}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Выполняем суммаризацию
    start_time = time.time()
    summary = summarize_text(prediction_data.text, prediction_data.model_type)
    processing_time = time.time() - start_time
    
    return PredictionResponse(
        id=1,
        user_id=current_user.id,
        input_text=prediction_data.text,
        summary=summary,
        model_used=prediction_data.model_type,
        cost=cost,
        processing_time=processing_time,
        created_at=datetime.now()
    )

@app.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = get_all_users(db)
    return users

@app.get("/")
def read_root():
    return {"message": "Welcome to Sci-Summ API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
