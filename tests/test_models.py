from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.models import Base, Food, Ingredient, Supplier, Worker


def test_festa_entities_persist_and_relate():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        supplier = Supplier(name="Horta da comunidade")
        ingredient = Ingredient(name="Tomate", unit="kg", supplier=supplier)
        food = Food(
            name="Sanduíche", description="Pão com tomate", sale_price=Decimal("12.50")
        )
        food.ingredients.append(ingredient)
        worker = Worker(name="Ana", category="Aluno")
        session.add_all([food, worker])
        session.commit()

        saved_food = session.scalar(select(Food).where(Food.name == "Sanduíche"))
        saved_worker = session.scalar(select(Worker).where(Worker.name == "Ana"))

        assert saved_food is not None
        assert saved_food.sale_price == Decimal("12.50")
        assert saved_food.ingredients[0].supplier.name == "Horta da comunidade"
        assert saved_worker is not None
        assert saved_worker.category == "Aluno"
