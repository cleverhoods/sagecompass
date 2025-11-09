from jsonschema import validate, ValidationError
import json, os
from app.utils.event_logger import log_event

class ValidationService:
    """
    Handles JSON schema validation and error logging for agent outputs.
    Can run in 'dev' mode (verbose logging) or 'prod' mode (quiet).
    """

    def __init__(self, dev_mode: bool = False):
        self.dev_mode = dev_mode or (os.getenv("SAGECOMPASS_ENV") == "dev")

    def validate_schema(data: dict, schema_path: str, agent: str = "system") -> bool:
        """
        Validate JSON data against a schema.
        - Returns True if valid, False otherwise.
        - In dev mode: logs success.
        - In prod: logs only failures/errors.
        """
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            validate(instance=data, schema=schema)
            if DEV_MODE:
                log_event("validation.success", {"agent": agent, "schema": schema_path})
            return True
        except ValidationError as e:
            log_event("validation.failed", {"agent": agent, "error": e.message, "schema": schema_path})
            return False
        except Exception as e:
            log_event("validation.error", {"agent": agent, "error": str(e), "schema": schema_path})
            return False

DEV_MODE = os.getenv("SAGECOMPASS_ENV", "prod").lower() == "dev"

