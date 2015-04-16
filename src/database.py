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


class LocationTable(object):
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    elevation = Column(Float, nullable=True)


class UDPBaseTable(object):


    id = Column(Integer, primary_key=True, nullable=False)
    status = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)


class UDPTable(UDPBaseTable, Base):
    __tablename__ = 'udp'


class UDPCoordTable(LocationTable, UDPBaseTable, Base):
    __tablename__ = 'udp_coords'


class TCPBaseTable(object):

    id = Column(Integer, primary_key=True, nullable=False)
    status = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)


class TCPTable(TCPBaseTable, Base):
    __tablename__ = 'tcp'


class TCPCoordTable(LocationTable, TCPBaseTable, Base):
    __tablename__ = 'tcp_coords'


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
