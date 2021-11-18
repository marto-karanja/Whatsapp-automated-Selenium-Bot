import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()

class GroupNames(Base):
    __tablename__ = 'GroupNames'

    id = Column(db.Integer, primary_key=True) 
    group_name = Column(db.String(1000))
    message = Column(db.String(1000))