from fastapi import FastAPI
from . import models
from .routers import auth, user, job_description, results, screening, resumes
from .database import engine
from fastapi.middleware.cors import CORSMiddleware
from .services.ai.embedding import embedding_service
from .services.ai.llm import llm_service


models.Base.metadata.create_all(bind=engine)#creating the tables in the database using the models defined in models.py

app = FastAPI(
    title="AIRI Auth API",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(job_description.router)
app.include_router(results.router)
app.include_router(screening.router)
app.include_router(resumes.router)











