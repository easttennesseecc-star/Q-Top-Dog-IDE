from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from . import Base

class User(Base):
    """Minimal User model for linking subscriptions.
    In environments using JSON-backed auth, this acts as a stub so
    SQLAlchemy relationships don't fail. Only an id is stored.
    """
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    # Reciprocal relationship required for Subscription.user back_populates
    subscription = relationship("Subscription", back_populates="user", uselist=False)
