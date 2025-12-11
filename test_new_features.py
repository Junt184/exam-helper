import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    print("Testing Login... 🔐")
    # Test Login
    try:
        resp = requests.post(f"{BASE_URL}/api/login", json={"username": "student", "password": "123"})
        assert resp.status_code == 401
        print("Login failed as expected with wrong password. ✅")
        
        resp = requests.post(f"{BASE_URL}/api/login", json={"username": "student", "password": "123123"})
        assert resp.status_code == 200
        print("Login successful! 🎉")
    except Exception as e:
        print(f"Login test failed: {e}")
        return

    print("\nTesting Create Quiz... ✍️")
    # Test Create Quiz
    quiz_name = "test_quiz_auto"
    content = """
    1. Python is a compiled language.
    A. True
    B. False
    Answer: B
    """
    try:
        resp = requests.post(f"{BASE_URL}/api/quizzes", json={"name": quiz_name, "content": content})
        if resp.status_code == 200:
            print(f"Quiz created successfully: {resp.json()} ✅")
        else:
            print(f"Quiz creation failed: {resp.text} ❌")
            return
    except Exception as e:
        print(f"Create quiz test failed: {e}")
        return

    print("\nTesting List Quizzes... 📚")
    # Test List Quizzes
    try:
        resp = requests.get(f"{BASE_URL}/api/quizzes")
        quizzes = resp.json()
        print(f"Quizzes found: {quizzes}")
        found = any(q['name'] == quiz_name for q in quizzes)
        if found:
            print("Test quiz found in list! ✅")
        else:
            print("Test quiz NOT found in list! ❌")
    except Exception as e:
        print(f"List quizzes test failed: {e}")

    print("\nTesting Get Quiz... 🧐")
    # Test Get Quiz
    try:
        resp = requests.get(f"{BASE_URL}/api/quizzes/{quiz_name}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Quiz data retrieved: {len(data)} questions. ✅")
        else:
            print(f"Get quiz failed: {resp.text} ❌")
    except Exception as e:
        print(f"Get quiz test failed: {e}")

if __name__ == "__main__":
    test_flow()
