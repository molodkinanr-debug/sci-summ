import sys
import os

print("🔍 Начало выполнения main.py...")
print(f"📁 Текущая директория: {os.getcwd()}")
print(f"🔧 Python path: {sys.path}")

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print("✅ Добавлена текущая директория в sys.path")

try:
    print("🔄 Пытаемся импортировать app.database.config...")
    from app.database.config import engine, SessionLocal, Base
    print("✅ app.database.config импортирован успешно")
    
    print("🔄 Пытаемся импортировать модели...")
    from app.models.user import User
    print("✅ User импортирован успешно")
    
    from app.models.account import AccountManager, Transaction
    print("✅ AccountManager и Transaction импортированы успешно")
    
    print("🎉 Все модули успешно импортированы!")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("📁 Проверяем структуру файлов:")
    for root, dirs, files in os.walk("."):
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files:
            if file.endswith(".py"):
                print(f"{subindent}{file}")
    sys.exit(1)

def init_database():
    print("🗄️ Начало инициализации базы данных...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы")
    
    db = SessionLocal()
    try:
        print("👤 Создаем администратора...")
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
            print("✅ Администратор создан")
            
            admin_account = AccountManager(user_id=admin.id, balance=1000.0)
            db.add(admin_account)
        
        print("👤 Создаем демо-пользователя...")
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
            print("✅ Демо-пользователь создан")
            
            demo_account = AccountManager(user_id=demo.id, balance=100.0)
            db.add(demo_account)
            
            transaction = Transaction(
                user_id=demo.id,
                amount=100.0,
                transaction_type="deposit",
                description="Initial balance"
            )
            db.add(transaction)
        
        db.commit()
        print("🎉 База данных инициализирована!")
        
        # Показываем результаты
        print("\n📊 Созданные пользователи:")
        users = db.query(User).all()
        for user in users:
            account = db.query(AccountManager).filter(AccountManager.user_id == user.id).first()
            print(f"   👤 {user.username} - баланс: {account.balance}")
            
    except Exception as e:
        print(f"❌ Ошибка при работе с БД: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("🔚 Завершение работы")

if __name__ == "__main__":
    print("🚀 Запуск функции init_database...")
    init_database()
    print("🏁 Скрипт завершен")
