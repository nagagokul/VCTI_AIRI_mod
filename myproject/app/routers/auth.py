from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, database, models, utils, oauth2
from datetime import datetime, timedelta, timezone

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    #  Create Access Token
    access_token = oauth2.create_access_token(
        data={"user_id": user.user_id}
    )

    #  Create Refresh Token
    refresh_token = oauth2.create_refresh_token()

    # Set refresh token expiry (example: 7 days)
    refresh_expiry = datetime.now(timezone.utc) + timedelta(days=7)

    #  Store Refresh Token in DB
    db_refresh_token = models.RefreshToken(
        user_id=user.user_id,
        token=refresh_token,
        expires_at=refresh_expiry
    )

    db.add(db_refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        }

@router.post("/refresh", response_model=schemas.Token)
def refresh_token(request: schemas.RefreshRequest,db: Session = Depends(database.get_db)):
    #  Find refresh token in DB
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == request.refresh_token
    ).first()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    #  Create new access token
    new_access_token = oauth2.create_access_token(
        data={"user_id": db_token.user_id}
    )

    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
        "user_id": db_token.user_id
    }

