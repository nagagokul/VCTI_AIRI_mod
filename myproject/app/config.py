from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    # DATABASE
    
    database_hostname: str
    database_port: int
    database_name: str
    database_username: str
    database_password: str

    
    # AUTH / JWT
    
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    
    # FILE PATHS
    
    upload_path: str = "app/uploads"
    json_template_path: str = "app/services/resume_structure.json"

    
    # OLLAMA SERVER
    
    base_url: str = "http://127.0.0.1:11434"

    
    # LLM MODELS
    
    arrange_llm: str = "llama3.2:3b"
    chat_llm: str = "llama3.2:3b"
    struct_llm: str = "llama3.2:3b"

    
    # EMBEDDING MODEL
    
    embedding_default_model: str = "snowflake-arctic-embed:latest"
    vector_size: int = 1024

    
    # ENV CONFIG
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()