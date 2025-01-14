# from sqlalchemy import Column, Integer, DateTime, func
#
# from ..databases import Base
#
#
# class BaseModel(Base):
#     __abstract__ = True
#
#     id = Column(Integer, primary_key=True)
#     created_at = Column(DateTime, nullable=False, default=func.now())
#     updated_at = Column(
#         DateTime,
#         onupdate=func.now(),
#     )
