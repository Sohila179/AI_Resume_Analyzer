from fastapi import (APIRouter,status,HTTPException,
                     Response,Path,Query,Header,Body,Request ,UploadFile,Form,File,Depends, Cookie)


from config import Settings
from database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Annotated
from models.user import User
from schemas.user import UserCreate,UserResponse ,userLogin
from services.security import hash_password ,verify_password
from fastapi.responses import JSONResponse
from services.security import create_access_token, get_user_id_from_token
from fastapi import Cookie
settings=Settings()

router = APIRouter()   

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy=Annotated[Session,Depends(get_db)]        

def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        user_id = get_user_id_from_token(access_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

@router.post(
    "/Register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(db: db_dependancy, user: UserCreate):

    result = db.execute(
        select(User).where(
            func.lower(User.email) == func.lower(user.email)
        )
    )

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    result = db.execute(
        select(User).where(
            func.lower(User.username) == func.lower(user.username)
        )
    )

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    if user.role not in ["job_seeker", "employer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be job_seeker or employer"
        )

    new_user = User(
        username=user.username,
        email=user.email.lower(),
        hashed_password=hash_password(user.password),
        role=user.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
def login_user(user: userLogin, db: db_dependancy):
    result = db.execute(select(User).where(func.lower(User.email) == func.lower(user.email)))
    existing_user = result.scalars().first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")

    if not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")

    token = create_access_token(existing_user.id)

    response = JSONResponse(
        content={"message": "Login successful"}
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=30 * 60
    )

    return response

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout_user(
    current_user: User = Depends(get_current_user)
):
    response = JSONResponse(
        content={
            "message": "Logged out successfully"
        }
    )

    response.delete_cookie(
        key="access_token"
    )

    return response