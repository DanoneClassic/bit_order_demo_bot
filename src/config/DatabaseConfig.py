import os
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    host: str
    port: int
    database: str
    username: str
    password: str
    min_size: int = 1
    max_size: int = 10
    max_queries: int = 50000
    max_inactive_connection_lifetime: float = 300.0

    @property
    def dsn(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        return cls(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            database=os.getenv('DB_NAME'),
            username=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            min_size=int(os.getenv('DB_MIN_SIZE', 1)),
            max_size=int(os.getenv('DB_MAX_SIZE', 10)),
            max_queries=int(os.getenv('DB_MAX_QUERIES', 50000)),
            max_inactive_connection_lifetime=float(os.getenv('DB_MAX_INACTIVE_TIME', 300.0))
        )

db_config = DatabaseConfig.from_env()