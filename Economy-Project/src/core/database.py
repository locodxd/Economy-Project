from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    wallet = Column(Float, default=0.0)
    bank = Column(Float, default=0.0)
    inventory = Column(JSON, default=dict)
    last_daily = Column(String, nullable=True)
    daily_streak = Column(Integer, default=0)

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # e.g., 'deposit', 'withdraw', 'transfer'
    timestamp = Column(String, nullable=False)

DATABASE_URL = 'sqlite:///../database/economy.db'

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def add_user(username):
    new_user = User(username=username)
    session.add(new_user)
    session.commit()

def get_user(username):
    return session.query(User).filter_by(username=username).first()

def add_transaction(user_id, amount, transaction_type, timestamp):
    new_transaction = Transaction(user_id=user_id, amount=amount, transaction_type=transaction_type, timestamp=timestamp)
    session.add(new_transaction)
    session.commit()

def get_transactions(user_id):
    return session.query(Transaction).filter_by(user_id=user_id).all()