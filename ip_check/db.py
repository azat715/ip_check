from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

Base = declarative_base()


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    ip = Column(Integer)
    city = Column(String)
    region = Column(String)
    country = Column(String)

    def __repr__(self):
        return "{ip='%s', city='%s', region='%s'," "country='%s'}" % (
            self.ip,
            self.city,
            self.region,
            self.country,
        )


eng = create_engine("sqlite:///history.db")

if not database_exists(eng.url):
    Base.metadata.create_all(eng)
    create_database(eng.url)

# создание конструктора сессий
Session = sessionmaker(bind=eng)

# управление сессиями
@contextmanager
def session_context():
    # создаем экземляр сессии
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise Exception("Ошибка записи в базу")
    finally:
        session.close()


class Controller:
    def __init__(self, s: Session):
        self.s = s

    def create(self, record):
        self.s.add(record)

    def __iter__(self):
        return iter(self.s.query(Item).all())


def add_item(record):
    with session_context() as session:
        rec = Item(
            ip=record.ip, city=record.city, region=record.region, country=record.country
        )
        Controller(session).create(rec)
        session.flush()


def show_items():
    with session_context() as session:
        for item in Controller(session):
            yield item
