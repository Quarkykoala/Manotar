import subprocess

# Define the curl command
url = 'http://localhost:8080/test_twilio'  # Assuming you're running the Flask app locally
command = ['curl', url]

# Execute the curl command
result = subprocess.run(command, capture_output=True, text=True)

# Print the output, error messages, and return code
print("Output:", result.stdout)
print("Error:", result.stderr)
print("Return code:", result.returncode)