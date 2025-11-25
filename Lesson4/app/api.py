import os
import sys
import hashlib
import time
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# Настройка БД
DATABASE_URL = "sqlite:///./sci_summ.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Простая функция хэширования
def get_password_hash(password: str) -> str:
    salt = "sci_summ_salt"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

# Модели БД
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Float, default=0.0)
    credit_limit = Column(Float, default=100.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Функции для работы с пользователями
def create_user(db: Session, user_data: dict):
    # Проверяем существование пользователя
    db_user = db.query(User).filter(
        (User.username == user_data["username"]) | 
        (User.email == user_data["email"])
    ).first()
    
    if db_user:
        return None
    
    # Создаем пользователя
    hashed_password = get_password_hash(user_data["password"])
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        full_name=user_data.get("full_name"),
        hashed_password=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Создаем аккаунт
    account = Account(user_id=user.id, balance=0.0)
    db.add(account)
    db.commit()
    
    return user

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# JWT настройки
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Pydantic схемы
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
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

# Функции аутентификации
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    
    # Списываем стоимость
    account.balance -= cost
    db.commit()
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
