"""
Base timeclass for Postgress timestmaps
"""
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime


class utcnow(expression.FunctionElement):
    """
    Defines datetime type in UTC
    """

    type = DateTime()


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    """
    Postgres UTC timestamp object
    """
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"
