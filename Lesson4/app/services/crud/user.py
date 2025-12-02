from sqlalchemy.orm import Session
from app.models.user import User
from app.models.account import Account
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_password_hash(password):
    return pwd_context.hash(password)

def create_user(db: Session, user_data):
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
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user
