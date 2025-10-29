import requests

API_URL = "http://127.0.0.1:8000/ask"  

def generate_answer_from_api(question):
    try:
        response = requests.post(API_URL, json={"question": question})
        response.raise_for_status()
        return response.json().get("answer", "")
    except Exception as e:
        return f"Error: {str(e)}"
