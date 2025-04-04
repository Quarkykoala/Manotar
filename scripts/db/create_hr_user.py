import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import HRUser

def create_hr_user(username, password):
    with app.app_context():
        hr_user = HRUser(username=username)
        hr_user.set_password(password)
        db.session.add(hr_user)
        db.session.commit()
        print(f"HR user {username} created successfully.")

if __name__ == "__main__":
    username = "admin"
    password = "password123"
    create_hr_user(username, password)
