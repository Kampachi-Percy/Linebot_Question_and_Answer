import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# sqliteのデータベースファイルを絶対パスで指定する
engine = sqlalchemy.create_engine("sqlite:////home/ubuntu/flask/LINE.db", echo=False, connect_args={"check_same_thread": False})

Base = declarative_base(bind=engine)

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"autoload": True}

class Question(Base):
    __tablename__ = "questions"
    __table_args__ = {"autoload": True}

class History(Base):
    __tablename__ = "histories"
    __table_args__ = {"autoload": True}

# セッションを作るクラスを作成
SessionClass = sessionmaker(engine, autocommit=False) 
session = SessionClass()