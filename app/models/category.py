from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    STATIC_CATEGORIES = {
        1: "Korrupció",
        2: "Jogállam",
        3: "Média és propaganda",
        4: "Társadalmi károkozás",
        5: "Külpolitika",
    }

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    sources = relationship("Source", back_populates="category")
