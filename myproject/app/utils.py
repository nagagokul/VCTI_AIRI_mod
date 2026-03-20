from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #telling passlib to use bcrypt for hashing the password

#this function will hash the password in db
def hash(password: str):
    return pwd_context.hash(password)

#this function will be used to verify the password during login. It takes the plain password from user and the hashed password from the db as input and returns True if they match, otherwise False.
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
