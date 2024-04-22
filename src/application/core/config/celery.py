import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class CelerySettings(BaseSettings):
    broker_url: str = "sqs://test:test@127.0.0.1:4566"
    broker_transport_options: dict[str, str] = {
        "region": "us-east-1",
        "predefined_queues": {
            "queue-1": {"url": "http://localhost:4566/000000000000/queue-1"}
        },
    }
    result_backend: str = "db+postgresql://sample:sample@localhost:5432/sample"
    task_default_queue: str = "queue-1"
    task_serializer: str = "json"
    accept_content: list[str] = ["application/json"]
    result_serializer: str = "json"
    worker_enable_remote_control: bool = False
    worker_hijack_root_logger: bool = False
    worker_prefetch_multiplier: int = 1
    task_reject_on_worker_lost: bool = True
    task_acks_late: bool = True
    enable_utc: bool = True
    broker_connection_retry_on_startup: bool = True
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENVIRONMENT', 'local')}",
        env_prefix="CELERY_",
        validate_default=False,
        extra="allow",
    )
