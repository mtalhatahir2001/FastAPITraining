from typing import List

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(10), nullable=False)
    first_name: Mapped[str] = mapped_column(String(32), nullable=True)
    last_name: Mapped[str] = mapped_column(String(32), nullable=True)
    password: Mapped[str] = mapped_column(String(8), nullable=False)

    todos: Mapped[List["Todo"]] = relationship(back_populates="todo_owner")


class Todo(Base):
    __tablename__ = "Todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(32), nullable=False)
    discription: Mapped[str] = mapped_column(String(100), nullable=True)
    priority: Mapped[int] = mapped_column(
        Integer(), CheckConstraint("priority >= 0 and priority <= 5")
    )
    user_id: Mapped[int] = mapped_column(Integer(), ForeignKey("Users.id"))

    todo_owner: Mapped[User] = relationship("todos")
