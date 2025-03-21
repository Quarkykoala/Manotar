import nltk
import os

# Set the download directory to a folder named 'nltk_data' in the current directory
nltk_data_dir = os.path.join(os.path.dirname(__file__), 'nltk_data')

# Create the directory if it doesn't exist
os.makedirs(nltk_data_dir, exist_ok=True)

# Set the NLTK data path
nltk.data.path.append(nltk_data_dir)

# Download the required NLTK data
nltk.download('punkt', download_dir=nltk_data_dir)
nltk.download('stopwords', download_dir=nltk_data_dir)

print("NLTK data downloaded successfully to:", nltk_data_dir)
