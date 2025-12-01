from sqlalchemy.orm import Session
from Lesson3.app.models.prediction import Prediction
from app.models.account import AccountManager, Transaction

def get_account_by_user_id(db: Session, user_id: int):
    return db.query(AccountManager).filter(AccountManager.user_id == user_id).first()

def deposit_to_account(db: Session, user_id: int, amount: float, description: str = "Deposit"):
    account = get_account_by_user_id(db, user_id)
    if account:
        account.balance += amount
        
        # Создаем транзакцию
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            transaction_type="deposit",
            description=description
        )
        db.add(transaction)
        db.commit()
        db.refresh(account)
        return account
    return None

def withdraw_from_account(db: Session, user_id: int, amount: float, description: str = "Withdrawal"):
    account = get_account_by_user_id(db, user_id)
    if account and (account.balance + account.credit_limit) >= amount:
        account.balance -= amount
        
        transaction = Transaction(
            user_id=user_id,
            amount=-amount,
            transaction_type="withdrawal",
            description=description
        )
        db.add(transaction)
        db.commit()
        db.refresh(account)
        return account
    return None

def get_transaction_history(db: Session, user_id: int, limit: int = 100):
    return db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.created_at.desc()).limit(limit).all()

def create_prediction_with_validation(db: Session, text: str, model_type: str, user_id: int):
    # Валидация
    if not text or len(text.strip()) < 10:
        raise ValueError("Text must be at least 10 characters")
    
    if model_type.lower() not in ['t5', 'bart', 'pegasus']:
        raise ValueError("Invalid model type. Use: t5, bart, pegasus")
    
    # Создание
    prediction = Prediction(
        text=text.strip(),
        model_type=model_type.lower(),
        user_id=user_id,
        status='pending'
    )
    
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction