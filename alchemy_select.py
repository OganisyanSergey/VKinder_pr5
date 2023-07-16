import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
db = 'postgresql://postgres:пароль@localhost:5432/usersvk'
engine = sq.create_engine(db, echo=True)
session = sessionmaker(bind=engine)
s = session()

class User(Base):
    __tablename__ = 'users_sent'

    id = sq.Column(sq.Integer, primary_key=True)
    users_id = sq.Column(sq.String)
    profiles_id = sq.Column(sq.String)

def create_tables():
    Base.metadata.create_all(engine)

def add_in_table(user_id, profile_id):
    s.add(User(users_id=user_id, profiles_id=profile_id))
    s.commit()

def select_of_table():
    result = s.query(User.users_id, User.profiles_id).all()
    return result
