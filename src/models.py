from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Column, ForeignKey, Numeric, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


food_ingredients = Table(
    "food_ingredients",
    Base.metadata,
    Column("food_id", ForeignKey("foods.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "ingredient_id",
        ForeignKey("ingredients.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
    Column("quantity", Numeric(10, 3), nullable=False, default=1.0),
)


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    contact: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    notes: Mapped[str] = mapped_column(String(500), default="", nullable=False)

    ingredients: Mapped[list[Ingredient]] = relationship(back_populates="supplier")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    unit: Mapped[str] = mapped_column(String(40), nullable=False)
    supplier_id: Mapped[int | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=True
    )

    supplier: Mapped[Supplier | None] = relationship(back_populates="ingredients")
    foods: Mapped[list[Food]] = relationship(
        secondary=food_ingredients, back_populates="ingredients"
    )


class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    ingredients: Mapped[list[Ingredient]] = relationship(
        secondary=food_ingredients, back_populates="foods"
    )


class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    contact: Mapped[str] = mapped_column(String(120), default="", nullable=False)
