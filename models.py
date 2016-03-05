import sqlalchemy
import sys, os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import Integer, Boolean, String, Column, DateTime, Enum, Text
from sqlalchemy.orm import sessionmaker
import configparser

Base = declarative_base()

class bot_comments(Base):
    __tablename__ = 'bot_comments'
    id = Column(Integer, primary_key=True)
    thing_id = Column(String(15), nullable=False)
    content = Column(String(10000), nullable=False)
    submitted = Column(Boolean, nullable=False)
    submitted_id = Column(String(15))

class bot_submissions(Base):
    __tablename__ = 'bot_submissions'
    id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    content = Column(String(15000))
    type = Column(String(10), nullable=False)
    subreddit = Column(String(50), nullable=False)
    submitted = Column(Boolean, nullable=False)    
    
class subreddit(Base):
    __tablename__ = 'subreddit'
    website = Column(String(10), primary_key=True)
    last_submission = Column(Integer)
    last_comment = Column(Integer)

class anet_member(Base):
    __tablename__ = 'anet_member'
    username = Column(String(50), primary_key=True)

class bot_comments_anetpool(Base):
    __tablename__ = 'bot_comments_anetpool'
    thread_id = Column(String(15))
    content = Column(String(10000), nullable=False)
    submitted = Column(Boolean, nullable=False)
    submitted_id = Column(String(15))
    edit_id = Column(Integer,primary_key=True, unique=True, nullable=False)


cfg_file = configparser.ConfigParser()
path_to_cfg = os.path.abspath(os.path.dirname(sys.argv[0]))
path_to_cfg = os.path.join(path_to_cfg, 'polarbytebot.cfg')
cfg_file.read(path_to_cfg)

engine = sqlalchemy.create_engine(
    cfg_file.get('database','system')+'://'+\
    cfg_file.get('database','username')+':'+\
    cfg_file.get('database','password')+'@'+\
    cfg_file.get('database','host')+'/'+\
    cfg_file.get('database','database'))

Session = sessionmaker(bind=engine, expire_on_commit=False)
session = Session()

