from abc import ABC
from typing import Any

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class ConfigurationWithSecrets(BaseModel, ABC):
    """
    Abstract model for configuration's secrets handling. Extending class has to implement `secrets` field with correspodning type.
    """

    def model_post_init(self, context: Any) -> None:
        self.secrets = self.get_secrets(secrets_file=context["secrets_file"])

    def get_secrets(self, secrets_file: str) -> BaseSettings:
        secrets_class = self.model_fields["secrets"].annotation
        secrets = secrets_class(_env_file=secrets_file)
        if secrets is None:
            raise ValueError(f"Secrets for {self.name} not found.")
        return secrets
