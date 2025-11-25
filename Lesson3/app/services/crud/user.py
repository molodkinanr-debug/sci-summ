from sqlalchemy.orm import Session
from app.models.user import User
from app.models.account import AccountManager

def create_user(db: Session, username: str, email: str, hashed_password: str, full_name: str = None):
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Создаем аккаунт для пользователя
    account = AccountManager(user_id=db_user.id)
    db.add(account)
    db.commit()
    
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
