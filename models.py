from sqlalchemy import Column, Integer, String, Numeric

from db import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    quote = Column(Numeric(10, 2)) ## Store 10 decimals in front of point and 2 positions after decimal point
    pe = Column(Numeric(10,2))
    dividend = Column(Numeric(10,2))
    ma50 = Column(Numeric(10,2))
    ma200 = Column(Numeric(10,2))