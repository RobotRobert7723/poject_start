from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


metadata = MetaData(schema="wb_auto_replies")


class Base(DeclarativeBase):
    metadata = metadata
