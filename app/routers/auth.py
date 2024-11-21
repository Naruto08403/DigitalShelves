from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models import Users, get_db
from random import randint
import pySMTP
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError,InvalidHashError

def get_password_hash(password):
    return pwd_context.hash(password)
# Secret key and algorithm for JWT
SECRET_KEY = "your_secret_key"  # Use a strong secret key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

authRouth = APIRouter(
    prefix="/auth",
    tags=["Authentications"]
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper function to hash password
def get_password_hash(password):
    return pwd_context.hash(password)

# Function to create a JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Helper function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Create JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to send OTP for signup confirmation
def sendSignupCode(code, email):
    try:
        TO = email
        FROM = 'arguellesruel51@gmail.com'
        passw = 'gvvh udbl kiru kamf'
        SUBJECT = 'Email Confirmation OTP'
        TEXT = f'''Please confirm your email with the code below:
            {code}'''
        pySMTP.send_email(FROM, passw, TO, SUBJECT, TEXT)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Function to generate a random OTP code
def generateCode():
    code = ''.join([str(randint(0, 9)) for _ in range(6)])
    return code

# Initialize the PasswordHasher for Argon2
ph = PasswordHasher()

@authRouth.post("/signup")
def signup(email: str, password: str, db: Session = Depends(get_db)):
    hashed_password = ph.hash(password)  # Hash password with Argon2
    code = generateCode()  # Assuming you already have a generateCode function
    user = db.query(Users).where(Users.email==email).first()
    if user and user.confirmed:
        return {'success':False, "message":"Email is already used. Please Login!"}
    elif user and not user.confirmed:
        user.code = code
    else:
        user = Users(email=email, password=hashed_password, code=str(code))
    db.add(user)
    db.commit()
    db.refresh(user)
    if sendSignupCode(code, email):  # Assuming you already have this function
        return {"success": True}
    return {'success':False, "message":"Plese Try again"}

@authRouth.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return {'success': False, "message": "Account Not Found"}
    if not user.confirmed:
        raise HTTPException(status_code=501,detail="Account Not Verrified")
    try:
        # Verify password using Argon2
        if ph.verify(user.password, password):
            # Generate JWT token upon successful login
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": email}, expires_delta=access_token_expires
            )
            print('done')
            return {
                'success': True,
                'access_token': access_token,
                'token_type': 'bearer'
            }
        else:
            return {'success': False, "message": "Incorrect Password"}
    except VerifyMismatchError:
        return {'success': False, "message": "Incorrect Password"}
    except InvalidHashError as e:
        print(e)
        return {'success': False, "message": "Incorrect Password"}

# Email confirmation endpoint
@authRouth.post("/verify-code")
def verify_email(email: str, code: str, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found.")
    
    # Check if the code matches
    if user.code != code:
        raise HTTPException(status_code=400, detail="Incorrect code.")

    # Confirm the user's email
    user.confirmed = True
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"success": True, "message": "Email confirmed successfully."}
