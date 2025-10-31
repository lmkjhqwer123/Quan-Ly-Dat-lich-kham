


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv

from routers.auth import auth_router
from routers.patient import update_patient_profile
from routers.patient import update_password
from routers.patient import book_appointment_for_patient
from routers.patient import book_appointment_for_me
from routers.patient import get_my_history
from routers.doctor import create_doctor
from routers.doctor import get_doctors
from routers.doctor import get_doctor
from routers.doctor import update_doctor
from routers.doctor import delete_doctor



load_dotenv()  # Load environment variables from .env file



app = FastAPI(

    title="QuanLyKhamBenh API",

    description="API for managing appointments in a hospital.",

    version="1.0.0"

)


app.include_router(auth_router.router)
app.include_router(update_patient_profile.router)
app.include_router(update_password.router)
app.include_router(book_appointment_for_patient.router)
app.include_router(book_appointment_for_me.router)
app.include_router(get_my_history.router)
app.include_router(create_doctor.router)
app.include_router(get_doctors.router)
app.include_router(get_doctor.router)
app.include_router(update_doctor.router)
app.include_router(delete_doctor.router)

app.mount("/Js", StaticFiles(directory="PresentationLayer/Js"), name="static_js")
app.mount("/", StaticFiles(directory="PresentationLayer/GUI"), name="presentation")

