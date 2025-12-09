from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    FB_APP_ID: str
    FB_APP_SECRET: str
    FB_API_VERSION: str = "v21.0"
    OAUTH_REDIRECT_URI: str
    FRONTEND_ORIGIN: str
    SESSION_SECRET: str
    OPENAI_API_KEY: str 


    class Config:
        env_file = ".env"

settings = Settings()
