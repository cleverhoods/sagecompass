import os
from jsonschema import validate as json_validate, ValidationError, SchemaError
from app.utils.logger import log


class ValidationService:
    """
    Handles JSON schema validation and event logging for agent outputs.
    Works directly with schema dicts (not file paths).

    Returns:
      • In prod mode → bool
      • In dev mode  → (bool, list[str])  for richer feedback
    """

    def __init__(self, dev_mode: bool = False):
        self.dev_mode = dev_mode or (os.getenv("SAGECOMPASS_ENV", "prod").lower() == "dev")

    def validate(self, data: dict, schema: dict, agent: str = "system"):
        """
        Validate JSON data against a schema dict.
        Returns:
          bool              (prod mode)
          (bool, errors[])  (dev mode)
        """
        errors = []
        try:
            json_validate(instance=data, schema=schema)
            if self.dev_mode:
                log("validation.success", {"agent": agent})
            return (True, []) if self.dev_mode else True

        except ValidationError as e:
            err = {
                "agent": agent,
                "error": e.message,
                "path": list(e.path),
                "schema_path": list(e.schema_path)
            }
            errors.append(err)
            log("validation.failure", err)
            return (False, errors) if self.dev_mode else False

        except SchemaError as e:
            err = {"agent": agent, "error": e.message, "type": "schema_error"}
            errors.append(err)
            log("validation.schema_error", err)
            return (False, errors) if self.dev_mode else False

        except Exception as e:
            err = {"agent": agent, "error": str(e), "type": "exception"}
            errors.append(err)
            log("validation.exception", err)
            return (False, errors) if self.dev_mode else False
