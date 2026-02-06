"""Nexus AI - Auth Router.

This module provides API endpoints for user authentication, including 
signup, login, and retrieval of the current user's profile.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from auth import verify_password, get_password_hash, create_access_token
from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse, Token, PasswordUpdate, UserUpdate
from dependencies import get_current_user
from config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


@router.post(
    "/signup", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account with a unique email and username. Passwords are securely hashed."
)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    """
    # Debug logging
    print(f"DEBUG: Signup attempt - Email: {user_data.email}, User: {user_data.username}, Pass Len: {len(user_data.password)}")
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post(
    "/login", 
    response_model=Token,
    summary="User login (JSON)",
    description="Authenticates with email and password to return a JWT access token."
)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    
    - Validates email exists
    - Verifies password
    - Returns access token
    """
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible login endpoint for Swagger UI testing.
    Uses form data instead of JSON.
    """
    # Find user by email (username field contains email)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me", 
    response_model=UserResponse,
    summary="Get current user",
    description="Retrieves the profile of the currently authenticated user."
)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description="Updates the authenticated user's username and/or email."
)
async def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update username and/or email for the current user.
    """
    # Check if new username is unique
    if data.username and data.username != current_user.username:
        existing = db.query(User).filter(User.username == data.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = data.username
    
    # Check if new email is unique
    if data.email and data.email != current_user.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = data.email
    
    # Merge settings if provided
    if data.settings is not None:
        current_settings = current_user.settings or {}
        if isinstance(current_settings, str):
             import json
             try:
                 current_settings = json.loads(current_settings)
             except:
                 current_settings = {}
        
        # Deep merge/update
        current_settings.update(data.settings)
        current_user.settings = current_settings
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, "settings")

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.put(
    "/password",
    summary="Update current user's password",
    description="Updates the authenticated user's password. Requires verification of the current password."
)
async def update_password(
    data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update password for the current user.
    """
    # Verify current password
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Hash and save new password
    current_user.hashed_password = get_password_hash(data.new_password)
    db.add(current_user)
    db.commit()
    
    return {"message": "Password updated successfully"}
@router.get("/me/api-key")
async def get_api_key(current_user: User = Depends(get_current_user)):
    """
    Get the Groq API key from environment for display in settings.
    """
    return {"api_key": settings.groq_api_key}
