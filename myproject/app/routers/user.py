from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, utils

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session= Depends(get_db)):

    #hashing the password before storing it in the database
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session= Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} was not found")
    return user

@router.post("/logout")
def logout(request: schemas.RefreshRequest,db: Session = Depends(get_db)):
    deleted = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == request.refresh_token
    ).delete()

    if deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    db.commit()

    return {"message": "Logged out successfully"}