from datetime import date, time, datetime

from pydantic import BaseModel, EmailStr, field_validator, constr
import re


class AppointmentBase(BaseModel):
    # fields available during both creating and reading
    doctor_name: constr(min_length=5)
    date: date
    time: time
    description: constr(min_length=20)


class AppointmentCreate(AppointmentBase):
    pass


class Appointment(AppointmentBase):
    # fields available only during reading
    id: int
    patient_id: int
    payment_link: str

    class Config:
        orm_mode = True  # so that the pydantic model can read data even if it is not a dict but an ORM model (or any
        # other object with attributes)


class PatientBase(BaseModel):
    # fields available during both creating and reading
    name: constr(min_length=5)
    phone: constr(min_length=10, max_length=10)
    email: EmailStr


class PatientCreate(PatientBase):
    pass


class PatientList(PatientBase):
    # fields available when listing patients
    id: int

    class Config:
        orm_mode = True  # so that the pydantic model can read data even if it is not a dict but an ORM model (or any
        # other object with attributes)


class PatientDetails(PatientBase):
    # fields available only during reading
    id: int
    appointments: list[Appointment] = []

    class Config:
        orm_mode = True  # so that the pydantic model can read data even if it is not a dict but an ORM model (or any
        # other object with attributes)


class UserBase(BaseModel):
    name: constr(min_length=5)
    email: EmailStr


class UserCreate(UserBase):
    password: constr(min_length=8)


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
