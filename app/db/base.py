"""Base Class for SQLAlchemy DB models"""

import re

from sqlalchemy.ext.declarative import declarative_base, declared_attr


class CustomBase:
    """Custom declarative_base for SQLAlchemy models"""

    @declared_attr
    def __tablename__(cls):
        """Generate `__tablename__` atribute automatically for SQLAlchemy models"""
        # Convert from CamelCase to lowercase snake_case
        # https://stackoverflow.com/a/1176023/728583
        return re.sub("(?!^)([A-Z]+)", r"_\1", cls.__name__).lower()


Base = declarative_base(cls=CustomBase)
