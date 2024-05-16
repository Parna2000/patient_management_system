from fastapi import FastAPI, Depends, HTTPException, Request, Form, Query, Path
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date, time, datetime

import crud
import database
import models
import schemas

app = FastAPI()

# create all tables and columns in our database
models.Base.metadata.create_all(bind=database.engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


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


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# PATIENTS
@app.get("/patients/", response_class=HTMLResponse)
def read_patients(request: Request, db: Session = Depends(get_db)):
    patients = crud.get_patients(db)
    return templates.TemplateResponse("patients/list.html", {"request": request, "patients": patients})


@app.get("/patients/{patient_id}", response_class=HTMLResponse)
def read_patient(request: Request, patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return templates.TemplateResponse("patients/detail.html", {"request": request, "patient": db_patient})


@app.get("/patients/name/", response_class=HTMLResponse)
def read_patients_by_name(request: Request, name: str = Query(...), db: Session = Depends(get_db)):
    # Here we are using Query, not Form, because a form element with a get request appends the input fields as
    # queries to the request URL.
    patients = crud.get_patients_by_name(db=db, name=name)
    if patients is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return templates.TemplateResponse("patients/list.html", {"request": request, "patients": patients})


@app.get("/patient/create", response_class=HTMLResponse)
def create_patient_form(request: Request):
    return templates.TemplateResponse("patients/create.html", {"request": request})


@app.post("/patients/create", response_class=HTMLResponse)
def create_patient(request: Request, name: str = Form(...), email: str = Form(...), phone: str = Form(...),
                   db: Session = Depends(get_db)):
    patient_data = schemas.PatientCreate(name=name, email=email, phone=phone)
    db_patient = crud.get_patient_by_email(db, email=patient_data.email)
    if db_patient:
        return templates.TemplateResponse("patients/create.html",
                                          {"request": request, "error": "Email already registered"})
    crud.create_patient(db=db, patient=patient_data)
    return RedirectResponse(url="/patients/", status_code=303)


@app.get("/patients/{patient_id}/update", response_class=HTMLResponse)
def update_patient_form(request: Request, patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return templates.TemplateResponse("patients/update.html", {"request": request, "patient": db_patient})


# @app.post("/patients/{patient_id}/update", response_class=HTMLResponse)
# def update_patient(request: Request, patient_id: int, name: str = Form(...), email: str = Form(...),
#                    phone: str = Form(...), db: Session = Depends(get_db)):
#     patient_data = schemas.PatientCreate(name=name, email=email, phone=phone)
#     db_patient = crud.get_patient_by_email(db, email=patient_data.email)
#     # print(patient_data.email)
#     if db_patient:
#         print("Error")
#         return templates.TemplateResponse("patients/update.html",
#                                           {"request": request, "error": "Email already registered"})
#     updated_patient = crud.update_patient(db=db, patient_id=patient_id, patient_update=patient_data)
#     if not updated_patient:
#         raise HTTPException(status_code=404, detail="Patient not found")
#     return RedirectResponse(url=f"/patients/{patient_id}", status_code=303)

@app.post("/patients/{patient_id}/update", response_class=HTMLResponse)
def update_patient(
    request: Request,
    patient_id: int = Path(...),
    name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    db: Session = Depends(get_db)
):
    patient_update = schemas.PatientCreate(name=name, email=email, phone=phone)
    try:

        if email:
            existing_patient = crud.get_patient_by_email(db, email=email)
            if existing_patient and existing_patient.id != patient_id:
                return templates.TemplateResponse("patients/update.html", {"request": request, "patient": patient_update, "error": "Email already exists."})

        updated_patient = crud.update_patient(db, patient_id=patient_id, patient_update=patient_update)
        if not updated_patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return RedirectResponse(url=f"/patients/{patient_id}", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("patients/update.html", {"request": request, "patient": patient_update, "error": str(e)})


@app.post("/patients/{patient_id}/delete", response_class=HTMLResponse)
def delete_patient(request: Request, patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    crud.delete_patient(db=db, patient_id=patient_id)
    return RedirectResponse(url="/patients/", status_code=303)


# APPOINTMENTS
@app.get("/appointments/", response_class=HTMLResponse)
def read_appointments(request: Request, db: Session = Depends(get_db)):
    appointments = crud.get_appointments(db)
    return templates.TemplateResponse("appointments/list.html", {"request": request, "appointments": appointments})


@app.get("/appointments/{patient_id}/create", response_class=HTMLResponse)
def create_appointment_form(request: Request, patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return templates.TemplateResponse("appointments/create.html", {"request": request, "patient": db_patient})


@app.post("/appointments/{patient_id}/create", response_class=HTMLResponse)
def create_appointment(request: Request, patient_id: int, doctor_name: str = Form(...), date: date = Form(...),
                       time: time = Form(...),
                       description: str = Form(...), db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    appointment_data = schemas.AppointmentCreate(doctor_name=doctor_name, date=date, time=time, description=description)
    db_appointment = crud.create_appointment(db=db, appointment=appointment_data, patient_id=patient_id)
    return RedirectResponse(url=f"/patients/{patient_id}", status_code=303)


@app.get("/appointments/{appointment_id}/update", response_class=HTMLResponse)
def update_appointment_form(request: Request, appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = crud.get_appointment(db, appointment_id=appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return templates.TemplateResponse("appointments/update.html", {"request": request, "appointment": db_appointment})


@app.post("/appointments/{appointment_id}/update", response_class=HTMLResponse)
def update_appointment(request: Request, appointment_id: int, doctor_name: str = Form(...), date: date = Form(...),
                       time: time = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    appointment_data = schemas.AppointmentCreate(doctor_name=doctor_name, date=date, time=time, description=description)
    db_appointment = crud.update_appointment(db=db, appointment_id=appointment_id, appointment_update=appointment_data)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return RedirectResponse(url=f"/appointments/", status_code=303)


@app.post("/appointments/{appointment_id}/delete", response_model=schemas.Appointment)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = crud.get_appointment(db, appointment_id=appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    crud.delete_appointment(db=db, appointment_id=appointment_id)
    return RedirectResponse(url=f"/appointments/", status_code=303)


# USERS
@app.get("/users/register", response_class=HTMLResponse)
def register_user_form(request: Request):
    return templates.TemplateResponse("users/register.html", {"request": request})


@app.post("/users/register", response_class=HTMLResponse)
def register_user(request: Request, name: str = Form(...), email: str = Form(...), phone: str = Form(...),
                  password: str = Form(...), db: Session = Depends(get_db)):
    user_data = schemas.UserCreate(name=name, email=email, phone=phone, password=password)
    db_user = crud.get_user_by_email(db, email=user_data.email)
    if db_user:
        return templates.TemplateResponse("users/register.html",
                                          {"request": request, "error": "Email already registered. Try logging in"})
    crud.create_user(db=db, user=user_data)
    return RedirectResponse(url="/", status_code=303)


@app.get("/users/login", response_class=HTMLResponse)
def login_user_form(request: Request):
    return templates.TemplateResponse("users/login.html", {"request": request})


@app.post("/users/login", response_class=HTMLResponse)
def login_user(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None or not crud.verify_password(password, db_user.hashed_password):
        return templates.TemplateResponse("users/login.html",
                                          {"request": request, "error": "Invalid email or password"})
    return RedirectResponse(url="/", status_code=303)


@app.get("/users/", response_class=HTMLResponse)
def read_users(request: Request, db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return templates.TemplateResponse("users/list.html", {"request": request, "users": users})
