import requests

def test_server():
    try:
        response = requests.get('http://localhost:8080/test')
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is it running?")
        return False

if __name__ == "__main__":
    test_server()
