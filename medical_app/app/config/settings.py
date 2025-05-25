from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    openai_org_id: str
    openai_project_id: str

    class Config:
        env_file = ".env"

settings = Settings()
