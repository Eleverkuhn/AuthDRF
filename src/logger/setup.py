import json, logging
from logging import Logger
from pathlib import Path


class LoggingConfig:
    path = Path("src/logger/config.json")
    logger_name = "AuthDRF"

    @property
    def logger(self) -> Logger:
        return logging.getLogger(self.logger_name)

    def load(self) -> None:
        with open(self.path) as json_config:
            config_file = json.load(json_config)
        return config_file
