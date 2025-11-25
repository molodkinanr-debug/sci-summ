from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
import re

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"

class RequestStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    INSUFFICIENT_FUNDS = "insufficient_funds"

class BaseEntity(ABC):
    def __init__(self, id: UUID):
        self._id = id
        self._created_at = datetime.now()
    
    @property
    def id(self) -> UUID:
        return self._id
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

class User(BaseEntity):
    def __init__(self, email: str, password_hash: str, name: str, 
                 role: UserRole = UserRole.USER):
        super().__init__(uuid4())
        self._email = email
        self._password_hash = password_hash
        self._name = name
        self._role = role
        self._is_active = True
    
    def _validate_email(self) -> None:
        """Проверяет корректность email."""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(self._email):
            raise ValueError("Invalid email format")
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        self._email = value
        self._validate_email()
    
    @property
    def password_hash(self) -> str:
        return self._password_hash
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def role(self) -> UserRole:
        return self._role
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "email": self._email,
            "name": self._name,
            "role": self._role.value,
            "is_active": self._is_active,
            "created_at": self._created_at.isoformat()
        }

class AccountManager(BaseEntity):
    """Управление балансами пользователей"""
    
    def __init__(self):
        super().__init__(uuid4())
        self._user_balances: Dict[UUID, float] = {}
        self._transaction_history: List['Transaction'] = []
    
    def create_account(self, user_id: UUID, initial_balance: float = 0.0) -> None:
        if user_id in self._user_balances:
            raise ValueError(f"Account for user {user_id} already exists")
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        self._user_balances[user_id] = initial_balance
    
    def get_balance(self, user_id: UUID) -> float:
        return self._user_balances.get(user_id, 0.0)
    
    def has_sufficient_balance(self, user_id: UUID, amount: float) -> bool:
        return self.get_balance(user_id) >= amount
    
    def deposit(self, user_id: UUID, amount: float, description: str = "") -> bool:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        if user_id not in self._user_balances:
            self.create_account(user_id, 0.0)
        
        self._user_balances[user_id] += amount
        transaction = Transaction(user_id, amount, TransactionType.DEPOSIT, description)
        self._transaction_history.append(transaction)
        return True
    
    def withdraw(self, user_id: UUID, amount: float, description: str = "") -> bool:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if not self.has_sufficient_balance(user_id, amount):
            return False
        
        self._user_balances[user_id] -= amount
        transaction = Transaction(user_id, amount, TransactionType.WITHDRAWAL, description)
        self._transaction_history.append(transaction)
        return True
    
    def refund(self, user_id: UUID, amount: float, description: str = "") -> bool:
        """Возврат средств пользователю"""
        return self.deposit(user_id, amount, f"REFUND: {description}")
    
    def get_transaction_history(self, user_id: Optional[UUID] = None) -> List['Transaction']:
        if user_id:
            return [t for t in self._transaction_history if t.user_id == user_id]
        return self._transaction_history.copy()
    
    def get_user_accounts(self) -> Dict[UUID, float]:
        """Получить все аккаунты пользователей"""
        return self._user_balances.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "total_users": len(self._user_balances),
            "total_balance": sum(self._user_balances.values()),
            "total_transactions": len(self._transaction_history),
            "created_at": self._created_at.isoformat()
        }

class PredictionHistory(BaseEntity):
    """Модель для истории предсказаний пользователя"""
    
    def __init__(self, user_id: UUID):
        super().__init__(uuid4())
        self._user_id = user_id
        self._predictions: List['PredictionRequest'] = []
    
    @property
    def user_id(self) -> UUID:
        return self._user_id
    
    def add_prediction(self, prediction: 'PredictionRequest') -> None:
        """Добавить запрос в историю"""
        self._predictions.append(prediction)
    
    def get_predictions(self, limit: Optional[int] = None) -> List['PredictionRequest']:
        """Получить историю предсказаний"""
        if limit:
            return self._predictions[-limit:]
        return self._predictions.copy()
    
    def get_successful_predictions(self) -> List['PredictionRequest']:
        """Получить только успешные предсказания"""
        return [p for p in self._predictions if p.status == RequestStatus.SUCCESS]
    
    def get_recent_predictions(self, count: int = 5) -> List['PredictionRequest']:
        """Получить последние N предсказаний"""
        return self._predictions[-count:]
    
    def get_predictions_by_status(self, status: RequestStatus) -> List['PredictionRequest']:
        """Получить предсказания по статусу"""
        return [p for p in self._predictions if p.status == status]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "user_id": str(self._user_id),
            "total_predictions": len(self._predictions),
            "successful_predictions": len(self.get_successful_predictions()),
            "failed_predictions": len(self.get_predictions_by_status(RequestStatus.ERROR)),
            "created_at": self._created_at.isoformat()
        }

class TransactionHistory(BaseEntity):
    """Модель для истории транзакций пользователя"""
    
    def __init__(self, user_id: UUID):
        super().__init__(uuid4())
        self._user_id = user_id
        self._transactions: List['Transaction'] = []
    
    @property
    def user_id(self) -> UUID:
        return self._user_id
    
    def add_transaction(self, transaction: 'Transaction') -> None:
        """Добавить транзакцию в историю"""
        self._transactions.append(transaction)
    
    def get_transactions(self, limit: Optional[int] = None) -> List['Transaction']:
        """Получить историю транзакций"""
        if limit:
            return self._transactions[-limit:]
        return self._transactions.copy()
    
    def get_transactions_by_type(self, transaction_type: TransactionType) -> List['Transaction']:
        """Получить транзакции по типу"""
        return [t for t in self._transactions if t.transaction_type == transaction_type]
    
    def get_total_deposits(self) -> float:
        """Получить общую сумму депозитов"""
        deposits = self.get_transactions_by_type(TransactionType.DEPOSIT)
        return sum(t.amount for t in deposits)
    
    def get_total_withdrawals(self) -> float:
        """Получить общую сумму списаний"""
        withdrawals = self.get_transactions_by_type(TransactionType.WITHDRAWAL)
        return sum(t.amount for t in withdrawals)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "user_id": str(self._user_id),
            "total_transactions": len(self._transactions),
            "total_deposits": self.get_total_deposits(),
            "total_withdrawals": self.get_total_withdrawals(),
            "created_at": self._created_at.isoformat()
        }

class MLModel(ABC):
    def __init__(self, name: str, version: str, cost_per_request: float):
        self._name = name
        self._version = version
        self._cost_per_request = cost_per_request
        self._is_active = True
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def cost_per_request(self) -> float:
        return self._cost_per_request
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    def activate(self) -> None:
        self._is_active = True
    
    def deactivate(self) -> None:
        self._is_active = False
    
    @abstractmethod
    def preprocess(self, input_data: Any) -> Any:
        pass
    
    @abstractmethod
    def predict(self, processed_data: Any) -> Any:
        pass
    
    @abstractmethod
    def postprocess(self, prediction: Any) -> Any:
        pass
    
    def process(self, input_data: Any) -> Any:
        if not self._is_active:
            raise RuntimeError("Model is not active")
        processed_data = self.preprocess(input_data)
        prediction = self.predict(processed_data)
        return self.postprocess(prediction)

class TextSummarizationModel(MLModel):
    def __init__(self, name: str, version: str, cost_per_request: float,
                 max_input_length: int):
        super().__init__(name, version, cost_per_request)
        self._max_input_length = max_input_length
    
    def preprocess(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
        
        cleaned_text = text.strip()
        if len(cleaned_text) > self._max_input_length:
            cleaned_text = cleaned_text[:self._max_input_length]
        
        return {
            "cleaned_text": cleaned_text,
            "length": len(cleaned_text),
            "tokens": cleaned_text.split()[:self._max_input_length]
        }
    
    def predict(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        text = processed_data["cleaned_text"]
        sentences = text.split('.')
        summary = '. '.join(sentences[:2]) + '.' if len(sentences) > 2 else text
        
        return {
            "original_length": len(text),
            "summary_length": len(summary),
            "summary_text": summary
        }
    
    def postprocess(self, prediction: Dict[str, Any]) -> str:
        return prediction["summary_text"]

class PDFFile(BaseEntity):
    def __init__(self, original_filename: str, file_path: str, file_size: int):
        super().__init__(uuid4())
        self._original_filename = original_filename
        self._file_path = file_path
        self._file_size = file_size
        self._extracted_text: Optional[str] = None
    
    @property
    def original_filename(self) -> str:
        return self._original_filename
    
    @property
    def file_path(self) -> str:
        return self._file_path
    
    @property
    def file_size(self) -> int:
        return self._file_size
    
    @property
    def extracted_text(self) -> Optional[str]:
        return self._extracted_text
    
    def set_extracted_text(self, text: str) -> None:
        if not text or not text.strip():
            raise ValueError("Extracted text cannot be empty")
        self._extracted_text = text
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "original_filename": self._original_filename,
            "file_size": self._file_size,
            "has_text": self._extracted_text is not None,
            "created_at": self._created_at.isoformat()
        }

class Transaction(BaseEntity):
    def __init__(self, user_id: UUID, amount: float, 
                 transaction_type: TransactionType, description: str = ""):
        super().__init__(uuid4())
        self._user_id = user_id
        self._amount = amount
        self._transaction_type = transaction_type
        self._description = description
    
    @property
    def user_id(self) -> UUID:
        return self._user_id
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @property
    def transaction_type(self) -> TransactionType:
        return self._transaction_type
    
    @property
    def description(self) -> str:
        return self._description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "user_id": str(self._user_id),
            "amount": self._amount,
            "transaction_type": self._transaction_type.value,
            "description": self._description,
            "created_at": self._created_at.isoformat()
        }

class PredictionRequest(BaseEntity):
    def __init__(self, user_id: UUID, pdf_file: PDFFile, model: MLModel):
        super().__init__(uuid4())
        self._user_id = user_id
        self._pdf_file = pdf_file
        self._model = model
        self._status = RequestStatus.PENDING
        self._cost = model.cost_per_request
        self._result: Optional[str] = None
        self._processed_at: Optional[datetime] = None
        self._error_message: Optional[str] = None
    
    @property
    def user_id(self) -> UUID:
        return self._user_id
    
    @property
    def status(self) -> RequestStatus:
        return self._status
    
    @property
    def cost(self) -> float:
        return self._cost
    
    @property
    def result(self) -> Optional[str]:
        return self._result
    
    @property
    def processed_at(self) -> Optional[datetime]:
        return self._processed_at
    
    @property
    def error_message(self) -> Optional[str]:
        return self._error_message
    
    def process_request(self, account_manager: AccountManager, 
                       prediction_history: PredictionHistory,
                       transaction_history: TransactionHistory) -> bool:
        """Обрабатывает запрос на предсказание"""
        try:
            # Проверяем баланс
            if not account_manager.has_sufficient_balance(self._user_id, self._cost):
                self._status = RequestStatus.INSUFFICIENT_FUNDS
                self._error_message = "Insufficient funds"
                prediction_history.add_prediction(self)
                return False
            
            # Списываем средства
            if not account_manager.withdraw(self._user_id, self._cost, f"Payment for {self._model.name}"):
                self._status = RequestStatus.ERROR
                self._error_message = "Failed to withdraw funds"
                prediction_history.add_prediction(self)
                return False
            
            # Добавляем транзакцию в историю
            transaction = Transaction(self._user_id, self._cost, TransactionType.PAYMENT, f"Payment for {self._model.name}")
            transaction_history.add_transaction(transaction)
            
            self._status = RequestStatus.PROCESSING
            
            # Проверяем наличие извлеченного текста
            if not self._pdf_file.extracted_text:
                self._status = RequestStatus.ERROR
                self._error_message = "No extracted text available in PDF"
                # Возвращаем средства
                account_manager.refund(self._user_id, self._cost, "No text in PDF")
                refund_transaction = Transaction(self._user_id, self._cost, TransactionType.REFUND, "Refund for no text")
                transaction_history.add_transaction(refund_transaction)
                prediction_history.add_prediction(self)
                return False
            
            # Обрабатываем запрос через модель
            try:
                self._result = self._model.process(self._pdf_file.extracted_text)
                self._status = RequestStatus.SUCCESS
                self._processed_at = datetime.now()
                prediction_history.add_prediction(self)
                return True
                
            except Exception as model_error:
                self._status = RequestStatus.ERROR
                self._error_message = f"Model processing error: {str(model_error)}"
                # Возвращаем средства при ошибке модели
                account_manager.refund(self._user_id, self._cost, f"Model error: {str(model_error)}")
                refund_transaction = Transaction(self._user_id, self._cost, TransactionType.REFUND, f"Refund for model error")
                transaction_history.add_transaction(refund_transaction)
                prediction_history.add_prediction(self)
                return False
                
        except Exception as e:
            self._status = RequestStatus.ERROR
            self._error_message = f"Unexpected error: {str(e)}"
            prediction_history.add_prediction(self)
            # Пытаемся вернуть средства в случае непредвиденной ошибки
            try:
                account_manager.refund(self._user_id, self._cost, f"System error: {str(e)}")
                refund_transaction = Transaction(self._user_id, self._cost, TransactionType.REFUND, f"Refund for system error")
                transaction_history.add_transaction(refund_transaction)
            except:
                pass  # Не можем ничего сделать, если возврат не удался
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "user_id": str(self._user_id),
            "pdf_file": self._pdf_file.to_dict(),
            "model_name": self._model.name,
            "status": self._status.value,
            "cost": self._cost,
            "result": self._result,
            "error_message": self._error_message,
            "processed_at": self._processed_at.isoformat() if self._processed_at else None,
            "created_at": self._created_at.isoformat()
        }

class SciSummSystem:
    """Основной класс системы для управления всеми компонентами"""
    
    def __init__(self):
        self.account_manager = AccountManager()
        self.prediction_histories: Dict[UUID, PredictionHistory] = {}
        self.transaction_histories: Dict[UUID, TransactionHistory] = {}
    
    def get_or_create_prediction_history(self, user_id: UUID) -> PredictionHistory:
        """Получить или создать историю предсказаний для пользователя"""
        if user_id not in self.prediction_histories:
            self.prediction_histories[user_id] = PredictionHistory(user_id)
        return self.prediction_histories[user_id]
    
    def get_or_create_transaction_history(self, user_id: UUID) -> TransactionHistory:
        """Получить или создать историю транзакций для пользователя"""
        if user_id not in self.transaction_histories:
            self.transaction_histories[user_id] = TransactionHistory(user_id)
        return self.transaction_histories[user_id]
    
    def process_prediction_request(self, prediction_request: PredictionRequest) -> bool:
        """Обработать запрос на предсказание"""
        prediction_history = self.get_or_create_prediction_history(prediction_request.user_id)
        transaction_history = self.get_or_create_transaction_history(prediction_request.user_id)
        
        return prediction_request.process_request(
            self.account_manager, 
            prediction_history, 
            transaction_history
        )
    
    def get_user_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        prediction_history = self.get_or_create_prediction_history(user_id)
        transaction_history = self.get_or_create_transaction_history(user_id)
        
        return {
            "user_id": str(user_id),
            "balance": self.account_manager.get_balance(user_id),
            "prediction_stats": prediction_history.to_dict(),
            "transaction_stats": transaction_history.to_dict()
        }

def main():
    """Основная функция для демонстрации системы"""
    print("Scientific Article Summarization System")
    print("System initialized successfully!")

if __name__ == "__main__":
    main()