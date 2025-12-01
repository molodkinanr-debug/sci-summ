import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(" Запуск системы Sci-Summ...")

try:
    from app.database.config import engine, SessionLocal, Base
    from app.models.user import User
    from app.models.account import Account
    from app.models.transaction import Transaction
    
    print(" Все модули успешно импортированы")
    
except ImportError as e:
    print(f" Ошибка импорта: {e}")
    print(" Доступные файлы:")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                print(f"   {os.path.join(root, file)}")
    sys.exit(1)

def init_database():
    """Инициализация базы данных"""
    print(" Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print(" Таблицы созданы")
    
    db = SessionLocal()
    try:
        # Создаем администратора
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@scisumm.com",
                hashed_password="hashed_admin123",
                full_name="System Administrator",
                is_admin=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(" Администратор создан")
            
            admin_account = Account(user_id=admin.id, balance=1000.0)
            db.add(admin_account)
        
        # Создаем демо-пользователя
        demo = db.query(User).filter(User.username == "demo").first()
        if not demo:
            demo = User(
                username="demo",
                email="demo@scisumm.com",
                hashed_password="hashed_demo123",
                full_name="Demo User"
            )
            db.add(demo)
            db.commit()
            db.refresh(demo)
            print(" Демо-пользователь создан")
            
            demo_account = Account(user_id=demo.id, balance=100.0)
            db.add(demo_account)
            
            transaction = Transaction(
                user_id=demo.id,
                amount=100.0,
                transaction_type="deposit",
                description="Initial balance"
            )
            db.add(transaction)
        
        db.commit()
        print(" База данных инициализирована!")
        
        # Показываем результаты
        print("\n Созданные пользователи:")
        users = db.query(User).all()
        for user in users:
            account = db.query(Account).filter(Account.user_id == user.id).first()
            print(f"    {user.username} - баланс: {account.balance}")
            
    except Exception as e:
        print(f" Ошибка: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
