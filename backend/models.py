from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    facebook_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String)
    access_token = Column(String)
    expires_in = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
