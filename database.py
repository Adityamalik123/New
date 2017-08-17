
import sys 
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, REAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship 
from sqlalchemy import create_engine 
Base= declarative_base()

class Company(Base):
	__tablename__ = 'company'
	name=Column(String(250),nullable=False)
	id=Column(Integer, primary_key=True)

class User(Base):
	__tablename__ = 'user'
	id=Column(Integer, primary_key=True)
	name=Column(String(250), nullable=False)
	email=Column(String(250), nullable=False)
	mobile=Column(String(20), nullable=False)
	company_id=Column(Integer, ForeignKey('company.id'))
	password=Column(String(250), nullable=False)
	otp=Column(String(250))
	mverifies=Column(Boolean, nullable=False)
	admin=Column(Boolean, nullable=False)
	company=relationship(Company)
	forgots=relationship("Forgot")

class Services(Base):
	__tablename__ = 'services'
	name=Column(String(250),nullable=False)
	id=Column(Integer, primary_key=True)
	
class ServicesJoined(Base):
	__tablename__='servicesJoined'
	services_id=Column(Integer, ForeignKey('services.id'))
	id=Column(Integer, primary_key=True)
	company_id=Column(Integer, ForeignKey('company.id'))
	company = relationship(Company)
	services=relationship(Services)

class Subscribe(Base):
	__tablename__='subscribe'
	id=Column(Integer, primary_key=True)
	email=Column(String(250), nullable=False)

class Tms(Base):
	__tablename__='testimonials'
	id=Column(Integer, primary_key=True)
	description=Column(String(500), nullable=False)
	user_id=Column(Integer, ForeignKey('user.id'))
	checked_admin=Column(Boolean, nullable=False)
	user=relationship(User)

	@property
	def serialize(self):
		return {
		   'description'    : self.description,
           'id'             : self.id,
           'user_id'        : self.user_id,
           'checked_admin'  : self.checked_admin,
       }

class Forgot(Base):
	__tablename__='forgot'
	id=Column(Integer, primary_key=True)
	user_id=Column(Integer, ForeignKey('user.id'))
	ustring=Column(String(250), nullable=False)
	extime=Column(REAL, nullable=False)


class Feedback(Base):
	__tablename__='feedback'
	id=Column(Integer, primary_key=True)
	user_id=Column(Integer, ForeignKey('user.id'))
	over_rating=Column(String(8), nullable=False)
	additional=Column(String(250))
	user=relationship(User)


	@property
	def serialize(self):
	   return {
           'additional'     : self.additional,
           'id'             : self.id,
           'user_id'        : self.user_id,
           'over_rating'    : self.over_rating,
       }

class Contact(Base):
	__tablename__='contact'
	id=Column(Integer, primary_key=True)
	name=Column(String(250), nullable=False)
	email=Column(String(250), nullable=False)
	message=Column(String(750), nullable=False)
	mobile=Column(String(20), nullable=False)
	company=Column(String(250), nullable=False)
	completed=Column(Boolean, nullable=False)


engine=create_engine('mysql+pymysql://sql12190078:6QLIPbV5vS@sql12.freemysqlhosting.net:3306/sql12190078')
Base.metadata.create_all(engine) 