from sqlalchemy.orm import Session
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
