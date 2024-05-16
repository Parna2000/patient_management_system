# pip install fastapi sqlalchemy psycopg2-binary stripe jinja2
# psycopg2-binary for connecting postgres to fastapi

from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

import crud
import database
import models
import schemas

app = FastAPI()

# create all tables and columns in our database
models.Base.metadata.create_all(bind=database.engine)


# to create a new session for each request
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# EXCEPTION HANDLING
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []
    for error in errors:
        loc = " -> ".join(map(str, error['loc']))
        msg = f"{loc}: {error['msg']}"
        error_messages.append(msg)
    return JSONResponse(
        status_code=422,
        content={"detail": error_messages},
    )


# PATIENTS
@app.post("/patients/", response_model=schemas.PatientDetails)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    db_patient = crud.get_patient_by_email(db, email=patient.email)
    if db_patient:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_patient(db=db, patient=patient)


@app.get("/patients/", response_model=list[schemas.PatientList])
def read_patients(db: Session = Depends(get_db)):
    patients = crud.get_patients(db)
    return patients


@app.get("/patients/{patient_id}", response_model=schemas.PatientDetails)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = crud.get_patient(db=db, patient_id=patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.get("/patients/name/{name}", response_model=list[schemas.PatientList])
def read_patients_by_name(name: str, db: Session = Depends(get_db)):
    patients = crud.get_patients_by_name(db=db, name=name)
    if patients is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patients


@app.put("/patients/{patient_id}/", response_model=schemas.PatientDetails)
def update_patient(patient_id: int, patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db_patient1 = crud.get_patient_by_email(db,email=patient.email)
    if db_patient1:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.update_patient(db=db, patient_id=patient_id, patient_update=patient)


@app.delete("/patients/{patient_id}/", response_model=schemas.PatientDetails)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.delete_patient(db=db, patient_id=patient_id)


# APPOINTMENTS
@app.post("/patients/{patient_id}/appointments/", response_model=schemas.Appointment)
def create_appointment(patient_id: int, appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.create_appointment(db=db, appointment=appointment, patient_id=patient_id)


@app.get("/appointments", response_model=list[schemas.Appointment])
def read_appointments(db: Session = Depends(get_db)):
    appointments = crud.get_appointments(db)
    return appointments


@app.put("/appointments/{appointment_id}/", response_model=schemas.Appointment)
def update_appointment(appointment_id: int, appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = crud.get_appointment(db, appointment_id=appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return crud.update_appointment(db=db, appointment_id=appointment_id, appointment_update=appointment)


@app.delete("/appointments/{appointment_id}/", response_model=schemas.Appointment)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = crud.get_appointment(db, appointment_id=appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return crud.delete_appointment(db=db, appointment_id=appointment_id)


# USER
@app.post("/users/register/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/users/login/")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user is None or not crud.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    return {"message": "Login successful"}


@app.get("/users/", response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users
