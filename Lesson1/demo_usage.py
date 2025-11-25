from object_model import *

def demonstrate_system():
    print("=== Демонстрация системы Sci-Summarizer ===\n")
    
    # Создание пользователя
    user = User("researcher@university.edu", "hashed_password", "Dr. Smith", balance=100.0)
    print(f"Создан пользователь: {user.name}, баланс: {user.balance}")
    
    # Создание ML модели
    model = TextSummarizationModel(
        name="sci-bart-summarizer",
        version="1.0", 
        cost_per_request=10.0,
        max_input_length=4096
    )
    print(f"Создана ML модель: {model.name}, стоимость запроса: {model.cost_per_request}")
    
    # Создание PDF файла
    pdf_file = PDFFile("quantum_physics_research.pdf", "/path/to/file.pdf", 2048000)
    
    # Имитация извлечения текста из PDF
    research_text = """
    В данной статье исследуются квантовые вычисления и их применение в машинном обучении. 
    Авторы предлагают новую архитектуру квантовых нейронных сетей, которая демонстрирует 
    повышенную эффективность на задачах оптимизации. Эксперименты показывают 30% улучшение 
    по сравнению с классическими подходами. Основные результаты включают теоретическое 
    обоснование и практическую реализацию предложенного метода.
    """
    pdf_file.set_extracted_text(research_text)
    
    # Создание запроса на обработку
    request = PredictionRequest(user.id, pdf_file, model)
    print(f"\nСоздан запрос на суммаризацию, стоимость: {request.cost}")
    
    # Обработка запроса
    success = request.process_request(user)
    
    if success:
        print("Запрос обработан успешно!")
        print(f"Результат суммаризации: {request.result}")
        print(f"Новый баланс пользователя: {user.balance}")
    else:
        print("Ошибка обработки запроса")
        print(f"Статус: {request.status}")
    
    # Демонстрация транзакции
    transaction = Transaction(
        user_id=user.id,
        amount=-request.cost,
        transaction_type=TransactionType.WITHDRAWAL,
        description="Оплата ML запроса на суммаризацию"
    )
    print(f"\nСоздана транзакция: {transaction.description}, сумма: {transaction.amount}")
    
    # Демонстрация принципов ООП
    print("\n=== Демонстрация принципов ООП ===")
    
    # Инкапсуляция
    print(f"Баланс через геттер: {user.balance}")
    
    # Наследование
    print(f"BaseEntity ID: {user.id}")
    print(f"BaseEntity created_at: {user.created_at}")
    
    # Полиморфизм
    def demonstrate_polymorphism(ml_model: MLModel, text: str):
        return ml_model.process(text)
    
    summary = demonstrate_polymorphism(model, research_text)
    print(f"Полиморфизм в действии: {summary[:50]}...")

if __name__ == "__main__":
    demonstrate_system()
    
    