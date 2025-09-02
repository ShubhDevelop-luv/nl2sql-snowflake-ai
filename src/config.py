import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ENV = os.getenv("ENV", "dev")
    PORT = int(os.getenv("PORT", "8000"))

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    AZURE_OPENAI_EMBED_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT", "text-embedding-3-small")

    SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
    SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
    SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
    SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
    SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
    SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")

    MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

    DEFAULT_LIMIT = int(os.getenv("DEFAULT_LIMIT", "200"))
    STATEMENT_TIMEOUT_SECONDS = int(os.getenv("STATEMENT_TIMEOUT_SECONDS", "20"))
    HARD_ROW_CAP = int(os.getenv("HARD_ROW_CAP", "10000"))

    SCHEMA_INDEX_PATH = os.getenv("SCHEMA_INDEX_PATH", "./.schema_index")

settings = Settings()

print(f"Loaded settings for environment: {settings.MONGO_URI}")   