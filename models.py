from database import Base
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from flask_login import UserMixin


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column('user_id', Integer, primary_key=True)
    username = Column(String(15), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(80))
    accounts = relationship("Account", backref="user", lazy="dynamic")
    uploads = relationship("Upload", backref="user", lazy="dynamic")
    transactions = relationship("Transaction", backref="user", lazy="dynamic")

    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password


class Account(Base):
    __tablename__ = 'accounts'
    id = Column('account_id', Integer, primary_key=True)
    name = Column('account_name', String)
    user_id = Column('user_id', Integer, ForeignKey(User.id))
    type_id = Column('account_type_id', Integer, ForeignKey('account_types.account_type_id'))
    type = relationship("AccountType")
    uploads = relationship("Upload", backref="account", lazy="dynamic", cascade="all, delete")
    transactions = relationship("Transaction", backref="account", cascade="all, delete")

    def __init__(self, id, name, user_id, type_id):
        self.id = id
        self.name = name
        self.user_id = user_id
        self.type_id = type_id


class AccountType(Base):
    __tablename__ = 'account_types'
    id = Column('account_type_id', Integer, primary_key=True)
    name = Column('account_type_name', String(40), nullable=False)
    csv_first_row = Column('csv_first_row', Integer, nullable=False)
    csv_name_column = Column('csv_name_column', Integer, nullable=False)
    csv_date_column = Column('csv_date_column', Integer, nullable=False)
    csv_date_format = Column('csv_date_format', String(15), nullable=False)
    csv_amount_column = Column('csv_amount_column', Integer, nullable=False)
    csv_amount_multiple = Column('csv_amount_multiple', Integer, nullable=False)
    accounts = relationship("Account", back_populates="type")


class Upload(Base):
    __tablename__ = 'uploads'
    id = Column('upload_id', Integer, primary_key=True)
    name = Column('csv_name', String(80), nullable=False)
    date = Column('upload_date', DateTime, nullable=False)
    account_id = Column('account_id', Integer, ForeignKey(Account.id), nullable=False)
    user_id = Column('user_id', Integer, ForeignKey(User.id), nullable=False)
    transactions = relationship("Transaction", backref="upload", cascade="all, delete")


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column('transaction_id', Integer, primary_key=True)
    name = Column('transaction_name', String, nullable=False)
    date = Column('transaction_date', Date, nullable=False)
    amount = Column('amount', Numeric, nullable=False)
    account_id = Column('account_id', Integer, ForeignKey(Account.id), nullable=False)
    upload_id = Column('upload_id', Integer, ForeignKey(Upload.id))
    user_id = Column('user_id', Integer, ForeignKey(User.id), nullable=False)
    category_id = Column('category_id', Integer, ForeignKey('transaction_categories.category_id'), default=1)
    category_override = Column('category_override', String(1), nullable=False, default='N')
    category = relationship("TransactionCategory")


class TransactionCategory(Base):
    __tablename__ = 'transaction_categories'
    id = Column('category_id', Integer, primary_key=True)
    name = Column('name', String(25), nullable=False)
    transactions = relationship("Transaction", back_populates="category")
