from datetime import datetime, timedelta
from jose import JWTError, jwt

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fake users database (temporary, just for testing)
fake_users_db = {
    "sai": {
        "username": "sai",
        "full_name": "Sai Krishna",
        "email": "sai@example.com",
        "hashed_password": "<some hashed password>",
        "disabled": False,
    }
}


# Secret key to encode and decode the JWT
SECRET_KEY = "your_secret_key_here"  # Replace with a stronger key later
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Validity of token

# Generate JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify JWT
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # You can check user/email here if needed
    except JWTError:
        return None
