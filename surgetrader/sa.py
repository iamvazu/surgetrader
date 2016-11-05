from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Float, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///sa.db', echo=True)
Base = declarative_base()


class Market(Base):
    __tablename__ = 'market'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String)
    low = Column(Float)
    time_created = Column(DateTime(timezone=True), server_default=func.now())


# sa.Base.metadata.create_all(sa.engine)
# from sqlalchemy.orm import sessionmaker
# Session = sessionmaker(bind=sa.engine)
# session.add(x)
# session = Session()
# session.add(x)
# session.commit()
