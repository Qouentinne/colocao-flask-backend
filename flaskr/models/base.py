from flask_sqlalchemy.model import Model
from sqlalchemy import Column, DateTime, inspect, func, String
from sqlalchemy.orm import as_declarative
from uuid import uuid4

@as_declarative()
class BaseModel(Model):
    __abstract__ = True
    __table_args__ = {'schema': 'public'}
    id = Column(String, default=lambda: str(uuid4()), primary_key=True, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=True)
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=True)

    def _asdict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}
    
