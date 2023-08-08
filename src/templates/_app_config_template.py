from src.schemas.app_config import AppConfigSchema


APP_CONFIG: dict = AppConfigSchema().model_dump()
