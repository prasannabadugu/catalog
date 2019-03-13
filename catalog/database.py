import sys
import os  # for files concept
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
# to use the columns,keys
from sqlalchemy.ext.declarative import declarative_base  # modle view control
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine  # to crate databse
Base = declarative_base()  # to control db


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class StateName(Base):
    __tablename__ = 'statename'
    id = Column(Integer, primary_key=True)
    st_name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="statename")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'st_name': self.st_name,
            'id': self.id
        }


class EclgName(Base):
    __tablename__ = 'eclgname'
    id = Column(Integer, primary_key=True)
    clg_name = Column(String(350), nullable=False)
    branches = Column(String(350), nullable=False)
    esta_year = Column(String(150))
    clg_phn = Column(Integer, nullable=False)
    clg_email = Column(String(90), nullable=False)
    web_site = Column(String(100))
    statenameid = Column(Integer, ForeignKey('statename.id'))
    statename = relationship(
        StateName, backref=backref('eclgname', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="eclgname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'clg_name': self.clg_name,
            'branches': self.branches,
            'esta_year': self.esta_year,
            'clg_phn': self.clg_phn,
            'clg_email': self.clg_email,
            'web_site': self.web_site,
            'id': self.id
        }

engin = create_engine('sqlite:///eng_clgs.db')
# to create database and insert values in
Base.metadata.create_all(engin)
