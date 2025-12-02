import os
import sys
import hashlib

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# Настройка БД
DATABASE_URL = "sqlite:///./sci_summ.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Простая функция хэширования (для демо, в продакшене используйте bcrypt)
def get_password_hash(password: str) -> str:
    salt = "sci_summ_salt"  # В реальном приложении используйте уникальную соль для каждого пользователя
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

# Функции
def create_user(session, user_data):
    # Проверяем существование пользователя
    db_user = session.query(User).filter(
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
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Создаем аккаунт
    account = Account(user_id=user.id, balance=0.0)
    session.add(account)
    session.commit()
    
    return user

def get_all_users(session):
    return session.query(User).all()

def authenticate_user(session, username: str, password: str):
    user = session.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

if __name__ == "__main__":
    print(" Запуск Sci-Summ системы...")
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    print(' База данных инициализирована')
    
    # Создаем тестовых пользователей
    test_users = [
        {"username": "admin", "email": "admin@scisumm.com", "password": "admin123", "full_name": "Admin User"},
        {"username": "demo", "email": "demo@scisumm.com", "password": "demo123", "full_name": "Demo User"},
        {"username": "test", "email": "test@scisumm.com", "password": "test123", "full_name": "Test User"}
    ]
    
    with SessionLocal() as session:
        # Создаем пользователей
        created_users = []
        for user_data in test_users:
            user = create_user(session, user_data)
            if user:
                created_users.append(user)
                print(f' Создан пользователь: {user.username}')
            else:
                print(f' Пользователь {user_data["username"]} уже существует')
        
        # Тестируем аутентификацию
        print('-------')
        print('Тестирование аутентификации:')
        test_auth = authenticate_user(session, "admin", "admin123")
        if test_auth:
            print(' Аутентификация admin/admin123: УСПЕХ')
        else:
            print(' Аутентификация admin/admin123: ОШИБКА')
        
        test_auth_wrong = authenticate_user(session, "admin", "wrongpassword")
        if not test_auth_wrong:
            print(' Аутентификация с неправильным паролем: ОЖИДАЕМАЯ ОШИБКА')
        
        # Получаем всех пользователей из БД
        users_from_db = get_all_users(session)
        
        print('-------')
        print('Пользователи из БД:')        
        for user in users_from_db:
            print(f' {user.username} ({user.email}) - активен: {user.is_active}')
    
    print(' Система готова к работе!')