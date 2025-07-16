from fastapi import FastAPI
from .config import ROOT_PATH
from .routes import api_users, api_membership, views, api_ai
from fastapi.staticfiles import StaticFiles

app = FastAPI(root_path=ROOT_PATH)

from .routes import api_users, api_membership, views, api_auth, api_patients, api_consultations, api_ai
app.include_router(api_users.router)
app.include_router(api_membership.router)
app.include_router(views.router)
app.include_router(api_auth.router)
app.include_router(api_patients.router)
app.include_router(api_consultations.router)
app.include_router(api_ai.router)

# Static files for templates (if needed)
app.mount("/static", StaticFiles(directory="elise/static"), name="static")
