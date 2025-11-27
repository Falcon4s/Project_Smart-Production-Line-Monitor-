from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Alias para compatibilidad con el código
    @property
    def hashed_password(self):
        return self.password_hash
    
    @hashed_password.setter
    def hashed_password(self, value):
        self.password_hash = value
    
    @property
    def is_active(self):
        return True