from sqlalchemy.orm import Session
from app.models.account import Account

def withdraw_from_account(db: Session, account_id: int, amount: float, description: str = ""):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise ValueError("Account not found")

    if account.balance < amount:
        raise ValueError("Insufficient funds")

    account.balance -= amount
    db.commit()
    return account
