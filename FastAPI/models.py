from sqlalchemy import Date, Time, Integer, String, Column, ForeignKey
from database import Base
from sqlalchemy.orm import relationship


class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")


class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String, index=True)
    date = Column(Date)
    time = Column(Time)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    description = Column(String, index=True)
    payment_link = Column(String, index=True)

    patient = relationship("Patient", back_populates="appointments")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
