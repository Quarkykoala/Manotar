<<<<<<< HEAD
import subprocess

# Define the curl command
url = 'http://localhost:8080/test_twilio'  # Ensure this matches your Flask app's endpoint
command = ['curl', url]

# Execute the curl command
result = subprocess.run(command, capture_output=True, text=True)

# Print the output, error messages, and return code
print("Output:", result.stdout)
print("Error:", result.stderr)
print("Return code:", result.returncode)
=======
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
>>>>>>> 684b464c7 (Initial commit)
