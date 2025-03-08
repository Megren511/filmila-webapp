from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_filmmaker = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    price = Column(Integer)  # Price in cents
    file_path = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="films")
    purchases = relationship("Purchase", back_populates="film")

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    film_id = Column(Integer, ForeignKey("films.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    film = relationship("Film", back_populates="purchases")

User.films = relationship("Film", back_populates="user")
