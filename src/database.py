from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, create_engine
from datetime import datetime
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class HuaweiTable(Base):

    __tablename__ = 'huawei'

    id = Column(Integer, primary_key=True, nullable=False)
    wifi = Column(String)
    mode = Column(String)
    signal = Column(String)
    roam = Column(String)
    connect = Column(String)
    connect6 = Column(String)
    connect4 = Column(String)
    timestamp = Column(DateTime, default=datetime.now)


class UDPTable(Base):
    __tablename__ = 'udp'

    id = Column(Integer, primary_key=True, nullable=False)
    status = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)


class TCPTable(Base):
    __tablename__ = 'tcp'

    id = Column(Integer, primary_key=True, nullable=False)
    status = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)


class DB(object):
    def __init__(self):
        self._engine = None

    def connect(self):
        if self._engine:
            return
        self._engine = create_engine('postgresql://networktester:networktestser@localhost/networktester', echo=False)

    def get_session(self):
        self.connect()
        Session = sessionmaker()
        Session.configure(bind=self._engine)
        return Session()

    def create_tables(self):
        self.connect()
        Base.metadata.create_all(self._engine)


DB = DB()