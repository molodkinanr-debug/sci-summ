import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print(" Тестирование Sci-Summ API...")
    
    # 1. Регистрация нового пользователя
    print("\n1.  Регистрация пользователя...")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            print("    Регистрация успешна")
            user_data = response.json()
            print(f"    Создан пользователь: {user_data['username']}")
        else:
            print(f"    Ошибка регистрации: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"    Ошибка подключения: {e}")
        return

    # 2. Авторизация
    print("\n2.  Авторизация...")
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print("    Авторизация успешна")
        print(f"    Получен токен: {access_token[:20]}...")
    else:
        print(f"    Ошибка авторизации: {response.status_code} - {response.text}")
        return
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 3. Проверка баланса
    print("\n3.  Проверка баланса...")
    response = requests.get(f"{BASE_URL}/accounts/balance", headers=headers)
    if response.status_code == 200:
        balance_data = response.json()
        print(f"    Баланс: {balance_data['balance']}")
    else:
        print(f"    Ошибка получения баланса: {response.status_code}")
    
    # 4. Пополнение баланса
    print("\n4.  Пополнение баланса...")
    response = requests.post(
        f"{BASE_URL}/accounts/deposit?amount=50&description=Test%20deposit",
        headers=headers
    )
    if response.status_code == 200:
        deposit_data = response.json()
        print(f"    Баланс пополнен: {deposit_data['new_balance']}")
    else:
        print(f"    Ошибка пополнения: {response.status_code}")
    
    # 5. Создание предсказания
    print("\n5.  Создание предсказания...")
    prediction_data = {
        "text": "This is a long scientific article about machine learning. It discusses various algorithms and their applications in different domains. The article covers supervised learning, unsupervised learning, and reinforcement learning techniques.",
        "model_type": "default"
    }
    
    response = requests.post(
        f"{BASE_URL}/predictions/summarize",
        json=prediction_data,
        headers=headers
    )
    
    if response.status_code == 200:
        prediction = response.json()
        print("    Предсказание создано")
        print(f"    Исходный текст: {prediction['input_text'][:50]}...")
        print(f"    Суммаризация: {prediction['summary']}")
        print(f"    Время обработки: {prediction['processing_time']:.2f} сек")
    else:
        print(f"    Ошибка предсказания: {response.status_code} - {response.text}")
    
    # 6. История предсказаний
    print("\n6.  История предсказаний...")
    response = requests.get(f"{BASE_URL}/predictions/history?limit=5", headers=headers)
    if response.status_code == 200:
        history = response.json()
        print(f"    Получено записей: {len(history)}")
    else:
        print(f"    Ошибка истории: {response.status_code}")
    
    print("\n Тестирование завершено!")

if __name__ == "__main__":
    test_api()
    