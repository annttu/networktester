import configuration
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, create_engine, Boolean
from datetime import datetime
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class LocationTable(object):
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    elevation = Column(Float, nullable=True)
    reported = Column(Boolean, nullable=False, default=False)


class HuaweiTable(LocationTable, Base):

    __tablename__ = '%shuawei_%s' % (configuration.table_prefix,
                                  configuration.table_suffix,)

    id = Column(Integer, primary_key=True, nullable=False)
    wifi = Column(String)
    mode = Column(String)
    signal = Column(String)
    roam = Column(String)
    connect = Column(String)
    connect6 = Column(String)
    connect4 = Column(String)
    timestamp = Column(DateTime, default=datetime.now)


class UDPBaseTable(object):


    id = Column(Integer, primary_key=True, nullable=False)
    status = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)


class UDPTable(UDPBaseTable, Base):
    __tablename__ = 'udp'


class UDPCoordTable(LocationTable, UDPBaseTable, Base):
    __tablename__ = '%sudp_%s' % (configuration.table_prefix,
                                  configuration.table_suffix,)


class TCPBaseTable(object):

    id = Column(Integer, primary_key=True, nullable=False)
    status = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)


class TCPTable(TCPBaseTable, Base):
    __tablename__ = 'tcp'


class TCPCoordTable(LocationTable, TCPBaseTable, Base):
    __tablename__ = '%stcp_%s' % (configuration.table_prefix,
                                  configuration.table_suffix,)


class DB(object):
    def __init__(self):
        self._engine = None

    def connect(self):
        if self._engine:
            return
        self._engine = create_engine('postgresql://%s:%s@%s/%s' % (configuration.database_username,
                                                                   configuration.database_password,
                                                                   configuration.database_hostname,
                                                                   configuration.database_database),
                                     echo=False, pool_recycle=1000, pool_size=2)

    def get_session(self):
        self.connect()
        Session = sessionmaker()
        Session.configure(bind=self._engine)
        return Session()

    def create_tables(self):
        self.connect()
        Base.metadata.create_all(self._engine)


DB = DB()
