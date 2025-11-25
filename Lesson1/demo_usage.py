"""
Демонстрация использования системы суммаризации научных статей
"""

from main import (User, AccountManager, TextSummarizationModel, PDFFile, 
                 PredictionRequest, UserRole, SciSummSystem, RequestStatus,
                 TransactionType)
from uuid import UUID

def demonstrate_basic_system():
    print("=== Демонстрация системы Sci-Summarizer ===\n")
    
    try:
        # Создаем основную систему
        system = SciSummSystem()
        print("✅ Система Sci-Summarizer инициализирована")
        
        # Создаем пользователя
        user = User("researcher@university.edu", "hashed_password", "Dr. Smith", UserRole.USER)
        print(f"✅ Пользователь создан: {user.name} ({user.email})")
        
        # Создаем аккаунт для пользователя с начальным балансом
        system.account_manager.create_account(user.id, 100.0)
        print(f"✅ Аккаунт создан с балансом: {system.account_manager.get_balance(user.id)}")
        
        # Создаем модель для суммаризации
        summarization_model = TextSummarizationModel(
            name="sci-summarizer-v1",
            version="1.0", 
            cost_per_request=15.0,
            max_input_length=2000
        )
        print(f"✅ Модель создана: {summarization_model.name} (стоимость: {summarization_model.cost_per_request})")
        
        # Создаем PDF файл с научной статьей
        pdf_file = PDFFile(
            original_filename="quantum_physics_research.pdf",
            file_path="/uploads/quantum_physics.pdf", 
            file_size=2048000
        )
        
        # Устанавливаем извлеченный текст из PDF
        research_text = """
            Quantum entanglement is a physical phenomenon that occurs when a pair or group of particles 
            is generated, interact, or share spatial proximity in a way such that the quantum state 
            of each particle of the pair or group cannot be described independently of the state of the others, 
            including when the particles are separated by a large distance. The topic of quantum entanglement 
            is at the heart of the disparity between classical and quantum physics: entanglement is a primary 
            feature of quantum mechanics not present in classical mechanics.
            
            Measurements of physical properties such as position, momentum, spin, and polarization performed 
            on entangled particles are found to be perfectly correlated. For example, if a pair of particles 
            is generated in such a way that their total spin is known to be zero, and one particle is found 
            to have clockwise spin on a certain axis, then the spin of the other particle, measured on the same 
            axis, will be found to be counterclockwise. Because of the nature of quantum measurement, however, 
            this behavior gives rise to effects that can appear paradoxical: any measurement of a property 
            of a particle can be seen as acting on that particle and will change the original quantum 
            property by some unknown amount.
        """
        pdf_file.set_extracted_text(research_text)
        print("✅ PDF файл создан и текст извлечен")
        
        # Создаем запрос на суммаризацию
        prediction_request = PredictionRequest(user.id, pdf_file, summarization_model)
        print(f"✅ Запрос на суммаризацию создан (стоимость: {prediction_request.cost})")
        
        # Обрабатываем запрос через систему
        print("\n--- Обработка запроса ---")
        if system.process_prediction_request(prediction_request):
            print("✅ Запрос успешно обработан!")
            print(f"📄 Результат суммаризации:\n{prediction_request.result}")
        else:
            print(f"❌ Ошибка обработки: {prediction_request.status.value}")
            if prediction_request.error_message:
                print(f"   Сообщение: {prediction_request.error_message}")
        
        # Показываем итоговую информацию
        print("\n--- Итоговая информация ---")
        user_stats = system.get_user_stats(user.id)
        
        print(f"💰 Баланс пользователя: {user_stats['balance']}")
        
        # История транзакций
        transaction_history = system.get_or_create_transaction_history(user.id)
        transactions = transaction_history.get_transactions()
        print(f"📊 Количество транзакций: {len(transactions)}")
        for transaction in transactions:
            print(f"  - {transaction.transaction_type.value}: {transaction.amount} ({transaction.description})")
        
        # История предсказаний
        prediction_history = system.get_or_create_prediction_history(user.id)
        predictions = prediction_history.get_predictions()
        print(f"🔮 Количество запросов: {len(predictions)}")
        for pred in predictions:
            status_icon = "✅" if pred.status == RequestStatus.SUCCESS else "❌"
            # Используем to_dict() для безопасного доступа к данным
            pred_dict = pred.to_dict()
            print(f"  {status_icon} {pred.status.value}: {pred_dict['model_name']} - {pred.cost}")
        
        # Статистика
        print(f"\n📈 Статистика пользователя:")
        pred_stats = user_stats['prediction_stats']
        trans_stats = user_stats['transaction_stats']
        print(f"  Успешных предсказаний: {pred_stats['successful_predictions']}")
        print(f"  Всего депозитов: {trans_stats['total_deposits']}")
        print(f"  Всего списаний: {trans_stats['total_withdrawals']}")
        
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()

def demonstrate_multiple_requests():
    """Демонстрация нескольких запросов с историей"""
    print("\n" + "="*50)
    print("Демонстрация нескольких запросов с историей")
    print("="*50)
    
    try:
        # Создаем систему
        system = SciSummSystem()
        user = User("student@university.edu", "hash123", "Alice Johnson", UserRole.USER)
        system.account_manager.create_account(user.id, 50.0)
        
        model = TextSummarizationModel(
            name="fast-summarizer",
            version="1.0",
            cost_per_request=10.0,
            max_input_length=1500
        )
        
        print(f"Начальный баланс: {system.account_manager.get_balance(user.id)}")
        
        # Первый запрос - успешный
        pdf1 = PDFFile("paper1.pdf", "/uploads/paper1.pdf", 1024000)
        pdf1.set_extracted_text("Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. " * 10)
        
        request1 = PredictionRequest(user.id, pdf1, model)
        print(f"\n📦 Запрос 1")
        if system.process_prediction_request(request1):
            print("✅ Успешно! Результат:", request1.result[:100] + "...")
        else:
            print(f"❌ Ошибка: {request1.status.value}")
        
        # Второй запрос - успешный  
        pdf2 = PDFFile("paper2.pdf", "/uploads/paper2.pdf", 1536000)
        pdf2.set_extracted_text("Deep learning uses neural networks with multiple layers to learn complex patterns in data. " * 15)
        
        request2 = PredictionRequest(user.id, pdf2, model)
        print(f"\n📦 Запрос 2")
        if system.process_prediction_request(request2):
            print("✅ Успешно! Результат:", request2.result[:100] + "...")
        else:
            print(f"❌ Ошибка: {request2.status.value}")
        
        # Пополняем баланс
        system.account_manager.deposit(user.id, 30.0, "Additional funding")
        print(f"\n💳 Баланс пополнен на 30.0")
        
        # Третий запрос - успешный после пополнения
        pdf3 = PDFFile("paper3.pdf", "/uploads/paper3.pdf", 2048000)
        pdf3.set_extracted_text("Natural language processing deals with text understanding and generation using computational methods. " * 20)
        
        request3 = PredictionRequest(user.id, pdf3, model)
        print(f"\n📦 Запрос 3")
        if system.process_prediction_request(request3):
            print("✅ Успешно! Результат:", request3.result[:100] + "...")
        else:
            print(f"❌ Ошибка: {request3.status.value}")
            if request3.error_message:
                print(f"   Причина: {request3.error_message}")
        
        # Показываем детальную историю
        print("\n" + "="*50)
        print("Детальная история системы")
        print("="*50)
        
        user_stats = system.get_user_stats(user.id)
        print(f"💰 Финальный баланс: {user_stats['balance']}")
        
        # Детальная история предсказаний
        prediction_history = system.get_or_create_prediction_history(user.id)
        predictions = prediction_history.get_predictions()
        
        print(f"\n📋 История предсказаний ({len(predictions)} запросов):")
        for i, pred in enumerate(predictions, 1):
            status_icon = "✅" if pred.status == RequestStatus.SUCCESS else "❌"
            # Используем to_dict() для безопасного доступа
            pred_dict = pred.to_dict()
            result_preview = pred.result[:50] + "..." if pred.result else "Нет результата"
            print(f"  {i}. {status_icon} {pred_dict['model_name']} - {pred.status.value}")
            print(f"     Стоимость: {pred.cost}, Результат: {result_preview}")
        
        # Детальная история транзакций
        transaction_history = system.get_or_create_transaction_history(user.id)
        transactions = transaction_history.get_transactions()
        
        print(f"\n💳 История транзакций ({len(transactions)} операций):")
        for i, trans in enumerate(transactions, 1):
            type_icon = "⬆️" if trans.transaction_type in [TransactionType.DEPOSIT, TransactionType.REFUND] else "⬇️"
            print(f"  {i}. {type_icon} {trans.transaction_type.value}: {trans.amount}")
            print(f"     Описание: {trans.description}")
            print(f"     Время: {trans.created_at.strftime('%H:%M:%S')}")
        
        # Сводная статистика
        print(f"\n📊 Сводная статистика:")
        pred_stats = user_stats['prediction_stats']
        trans_stats = user_stats['transaction_stats']
        print(f"  Всего запросов: {pred_stats['total_predictions']}")
        print(f"  Успешных: {pred_stats['successful_predictions']}")
        print(f"  Неудачных: {pred_stats['failed_predictions']}")
        print(f"  Общие депозиты: {trans_stats['total_deposits']}")
        print(f"  Общие списания: {trans_stats['total_withdrawals']}")
        
    except Exception as e:
        print(f"❌ Ошибка в демо: {e}")
        import traceback
        traceback.print_exc()

def demonstrate_error_cases():
    """Демонстрация обработки ошибок"""
    print("\n" + "="*50)
    print("Демонстрация обработки ошибок")
    print("="*50)
    
    try:
        system = SciSummSystem()
        user = User("test@university.edu", "hash456", "Test User", UserRole.USER)
        system.account_manager.create_account(user.id, 5.0)  # Маленький баланс
        
        model = TextSummarizationModel(
            name="test-model",
            version="1.0",
            cost_per_request=10.0,  # Стоимость больше баланса
            max_input_length=1000
        )
        
        # Запрос с недостаточным балансом
        pdf = PDFFile("test.pdf", "/uploads/test.pdf", 1024000)
        pdf.set_extracted_text("This is a test document for demonstration purposes.")
        
        request = PredictionRequest(user.id, pdf, model)
        print(f"Баланс: {system.account_manager.get_balance(user.id)}, Стоимость: {request.cost}")
        
        if not system.process_prediction_request(request):
            print(f"❌ Ожидаемая ошибка: {request.status.value}")
            print(f"   Сообщение: {request.error_message}")
        
        # Показываем что запрос все равно добавлен в историю
        prediction_history = system.get_or_create_prediction_history(user.id)
        print(f"Запросы в истории: {len(prediction_history.get_predictions())}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    demonstrate_basic_system()
    demonstrate_multiple_requests()
    demonstrate_error_cases()

    