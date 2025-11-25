from datetime import datetime
from typing import List

class UserRole():
    USER = "user"
    ADMIN = "admin"

class TransactionType():
    DEPOSIT = "deposit"  # Пополнение
    WITHDRAWAL = "withdrawal"  # Списание за запрос
    ADMIN_DEPOSIT = "admin_deposit"  # Админское пополнение

class RequestStatus():
    """Статусы ML запросов"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    VALIDATION_ERROR = "validation_error"

class FileValidationStatus():
    """Статусы валидации файлов"""
    VALID = "valid"
    INVALID_FORMAT = "invalid_format"
    INVALID_SIZE = "invalid_size"
    CORRUPTED = "corrupted"
    UNSUPPORTED_LANGUAGE = "unsupported_language"


class TextSummarizationModel():
    """Конкретная реализация ML модели для суммаризации текста"""
        
    def __init__(self, name: str, version: str, cost_per_request: float,
                 max_input_length: int, supported_languages: List[str]):
        super().__init__(name, version, cost_per_request)
        self._max_input_length = max_input_length
        self._supported_languages = supported_languages
        