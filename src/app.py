from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import sys

import streamlit as st
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database import SessionLocal, engine, initialize_database
from src.models import Food, Ingredient, Supplier, Worker

st.set_page_config(page_title="Festa IFC Blumenau", page_icon="🎉", layout="wide")

WORKER_CATEGORIES = ["Aluno", "Pai/mãe/responsável", "Servidor"]
PAGES = [
    "Visão geral",
    "Alimentos",
    "Insumos doados",
    "Fornecedores/doadores",
    "Trabalhadores",
]


def money(value: Decimal) -> str:
    return f"R$ {value:.2f}".replace(".", ",")


def commit(session: Session) -> bool:
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        st.error(
            "Não foi possível salvar. Verifique nomes duplicados e se o registro "
            "não está sendo usado por outro cadastro."
        )
        return False


def load_records(session: Session, model: type) -> list:
    return list(session.scalars(select(model).order_by(model.id)))


def display_table(records: list, columns: dict[str, str]) -> None:
    st.dataframe(
        [{label: getter(record) for label, getter in columns.items()} for record in records],
        width="stretch",
        hide_index=True,
    )


def record_selector(records: list, label: str):
    if not records:
        st.info("Ainda não há registros cadastrados.")
        return None
    labels = {record.id: f"{record.name} (#{record.id})" for record in records}
    record_id = st.selectbox(label, list(labels), format_func=labels.get)
    return next(record for record in records if record.id == record_id)


def operation_selector() -> str:
    return st.radio("Ação", ["Cadastrar", "Editar", "Excluir"], horizontal=True)


def render_suppliers(session: Session) -> None:
    st.header("Fornecedores e doadores")
    records = load_records(session, Supplier)
    display_table(
        records,
        {
            "Nome": lambda row: row.name,
            "Contato": lambda row: row.contact,
            "Observações": lambda row: row.notes,
        },
    )
    action = operation_selector()
    selected = record_selector(records, "Cadastro") if action != "Cadastrar" else None
    if action != "Cadastrar" and selected is None:
        return
    if action == "Excluir":
        if selected and st.button("Excluir fornecedor/doador", type="primary"):
            session.delete(selected)
            if commit(session):
                st.success("Fornecedor/doador excluído.")
                st.rerun()
        return

    with st.form("supplier_form"):
        name = st.text_input("Nome", value=selected.name if selected else "")
        contact = st.text_input("Contato (opcional)", value=selected.contact if selected else "")
        notes = st.text_area("Observações (opcional)", value=selected.notes if selected else "")
        submitted = st.form_submit_button("Salvar")
    if submitted:
        if not name.strip():
            st.error("Informe o nome.")
            return
        supplier = selected or Supplier()
        supplier.name = name.strip()
        supplier.contact = contact.strip()
        supplier.notes = notes.strip()
        session.add(supplier)
        if commit(session):
            st.success("Cadastro salvo.")
            st.rerun()


def render_ingredients(session: Session) -> None:
    st.header("Insumos doados")
    records = load_records(session, Ingredient)
    display_table(
        records,
        {
            "Insumo": lambda row: row.name,
            "Unidade": lambda row: row.unit,
            "Doador": lambda row: row.supplier.name if row.supplier else "Não informado",
        },
    )
    suppliers = load_records(session, Supplier)
    action = operation_selector()
    selected = record_selector(records, "Insumo") if action != "Cadastrar" else None
    if action != "Cadastrar" and selected is None:
        return
    if action == "Excluir":
        if selected and st.button("Excluir insumo", type="primary"):
            session.delete(selected)
            if commit(session):
                st.success("Insumo excluído.")
                st.rerun()
        return

    supplier_labels = {None: "Não informado"}
    supplier_labels.update({supplier.id: supplier.name for supplier in suppliers})
    default_supplier = selected.supplier_id if selected else None
    with st.form("ingredient_form"):
        name = st.text_input("Nome", value=selected.name if selected else "")
        unit = st.text_input("Unidade (ex.: kg, pacote, unidade)", value=selected.unit if selected else "")
        supplier_id = st.selectbox(
            "Fornecedor/doador",
            list(supplier_labels),
            index=list(supplier_labels).index(default_supplier)
            if default_supplier in supplier_labels
            else 0,
            format_func=supplier_labels.get,
        )
        submitted = st.form_submit_button("Salvar")
    if submitted:
        if not name.strip() or not unit.strip():
            st.error("Informe o nome e a unidade do insumo.")
            return
        ingredient = selected or Ingredient()
        ingredient.name = name.strip()
        ingredient.unit = unit.strip()
        ingredient.supplier_id = supplier_id
        session.add(ingredient)
        if commit(session):
            st.success("Insumo salvo.")
            st.rerun()


def render_foods(session: Session) -> None:
    st.header("Alimentos à venda")
    records = load_records(session, Food)
    display_table(
        records,
        {
            "Alimento": lambda row: row.name,
            "Preço de venda": lambda row: money(row.sale_price),
            "Insumos": lambda row: ", ".join(item.name for item in row.ingredients) or "—",
            "Descrição": lambda row: row.description,
        },
    )
    ingredients = load_records(session, Ingredient)
    action = operation_selector()
    selected = record_selector(records, "Alimento") if action != "Cadastrar" else None
    if action != "Cadastrar" and selected is None:
        return
    if action == "Excluir":
        if selected and st.button("Excluir alimento", type="primary"):
            session.delete(selected)
            if commit(session):
                st.success("Alimento excluído.")
                st.rerun()
        return

    if not ingredients:
        st.caption("Cadastre insumos antes de associá-los aos alimentos.")
    ingredient_options = {item.id: f"{item.name} ({item.unit})" for item in ingredients}
    current_ids = [item.id for item in selected.ingredients] if selected else []
    with st.form("food_form"):
        name = st.text_input("Nome", value=selected.name if selected else "")
        description = st.text_area(
            "Descrição (opcional)", value=selected.description if selected else ""
        )
        sale_price = st.number_input(
            "Preço de venda (R$)",
            min_value=0.01,
            value=float(selected.sale_price) if selected else 1.0,
            step=0.5,
        )
        ingredient_ids = st.multiselect(
            "Insumos utilizados",
            list(ingredient_options),
            default=current_ids,
            format_func=ingredient_options.get,
        )
        submitted = st.form_submit_button("Salvar")
    if submitted:
        if not name.strip():
            st.error("Informe o nome do alimento.")
            return
        food = selected or Food()
        food.name = name.strip()
        food.description = description.strip()
        food.sale_price = Decimal(str(sale_price))
        food.ingredients = [item for item in ingredients if item.id in ingredient_ids]
        session.add(food)
        if commit(session):
            st.success("Alimento salvo.")
            st.rerun()


def render_workers(session: Session) -> None:
    st.header("Trabalhadores da festa")
    records = load_records(session, Worker)
    display_table(
        records,
        {
            "Nome": lambda row: row.name,
            "Categoria": lambda row: row.category,
            "Contato": lambda row: row.contact,
        },
    )
    action = operation_selector()
    selected = record_selector(records, "Trabalhador") if action != "Cadastrar" else None
    if action != "Cadastrar" and selected is None:
        return
    if action == "Excluir":
        if selected and st.button("Excluir trabalhador", type="primary"):
            session.delete(selected)
            if commit(session):
                st.success("Trabalhador excluído.")
                st.rerun()
        return

    with st.form("worker_form"):
        name = st.text_input("Nome", value=selected.name if selected else "")
        category = st.selectbox(
            "Categoria",
            WORKER_CATEGORIES,
            index=WORKER_CATEGORIES.index(selected.category)
            if selected and selected.category in WORKER_CATEGORIES
            else 0,
        )
        contact = st.text_input("Contato (opcional)", value=selected.contact if selected else "")
        submitted = st.form_submit_button("Salvar")
    if submitted:
        if not name.strip():
            st.error("Informe o nome.")
            return
        worker = selected or Worker()
        worker.name = name.strip()
        worker.category = category
        worker.contact = contact.strip()
        session.add(worker)
        if commit(session):
            st.success("Trabalhador salvo.")
            st.rerun()


def render_overview(session: Session) -> None:
    st.title("Festa IFC Blumenau")
    st.write(
        "Organize os alimentos que serão vendidos, os insumos recebidos em doação, "
        "seus fornecedores e as pessoas que vão trabalhar no evento."
    )
    foods = load_records(session, Food)
    ingredients = load_records(session, Ingredient)
    suppliers = load_records(session, Supplier)
    workers = load_records(session, Worker)
    cols = st.columns(4)
    cols[0].metric("Alimentos", len(foods))
    cols[1].metric("Insumos doados", len(ingredients))
    cols[2].metric("Fornecedores/doadores", len(suppliers))
    cols[3].metric("Trabalhadores", len(workers))
    if foods:
        st.subheader("Cardápio e preços")
        display_table(
            foods,
            {
                "Alimento": lambda row: row.name,
                "Preço de venda": lambda row: money(row.sale_price),
                "Insumos": lambda row: ", ".join(item.name for item in row.ingredients) or "—",
            },
        )


def main() -> None:
    st.sidebar.title("Festa IFC")
    page = st.sidebar.radio("Menu", PAGES)
    try:
        initialize_database(engine)
        with SessionLocal() as session:
            if page == "Visão geral":
                render_overview(session)
            elif page == "Alimentos":
                render_foods(session)
            elif page == "Insumos doados":
                render_ingredients(session)
            elif page == "Fornecedores/doadores":
                render_suppliers(session)
            else:
                render_workers(session)
    except SQLAlchemyError as error:
        st.error(f"Erro ao acessar o banco de dados: {error}")
        st.info("Confira a configuração DATABASE_URL e a disponibilidade do banco.")


if __name__ == "__main__":
    main()
