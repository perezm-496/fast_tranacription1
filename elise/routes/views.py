from fastapi import APIRouter, Request, Form, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from elise.database import db
from elise.utils.auth import decode_access_token
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/views", tags=["views"])
templates = Jinja2Templates(directory="elise/templates")
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except Exception:
        return None

@router.get("/login", response_class=HTMLResponse)
async def login_view(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_post(request: Request, email: str = Form(...)):
    user = db.users.find_one({"email": email})
    if user:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "name": user["name"],
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "User not found"
    })

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_view(
    request: Request, 
    current_user: Optional[str] = Depends(get_current_user),
    token: Optional[str] = Query(None)
):
    # Try to get user from token in query params if not in header
    if not current_user and token:
        try:
            payload = decode_access_token(token)
            email: str = payload.get("sub")
            if email:
                current_user = email
        except Exception:
            pass
    
    # If still no user, return login page
    if not current_user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Please login to access the dashboard"
        })
    
    user = db.users.find_one({"email": current_user})
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "User not found"
        })
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "name": user.get("name", current_user),
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "current_user": current_user
    })

@router.get("/create-patient", response_class=HTMLResponse)
async def create_patient_view(
    request: Request,
    current_user: Optional[str] = Depends(get_current_user),
    token: Optional[str] = Query(None)
):
    # Try to get user from token in query params if not in header
    if not current_user and token:
        try:
            payload = decode_access_token(token)
            email: str = payload.get("sub")
            if email:
                current_user = email
        except Exception:
            pass
    
    # If still no user, return login page
    if not current_user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Please login to create a patient"
        })
    
    return templates.TemplateResponse("create_patient.html", {
        "request": request
    })

@router.get("/patient-dashboard", response_class=HTMLResponse)
async def patient_dashboard_view(
    request: Request,
    current_user: Optional[str] = Depends(get_current_user),
    token: Optional[str] = Query(None)
):
    # Try to get user from token in query params if not in header
    if not current_user and token:
        try:
            payload = decode_access_token(token)
            email: str = payload.get("sub")
            if email:
                current_user = email
        except Exception:
            pass
    
    # If still no user, return login page
    if not current_user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Please login to view patient dashboard"
        })
    
    return templates.TemplateResponse("patient_dashboard.html", {
        "request": request
    })

@router.get("/add-consultation", response_class=HTMLResponse)
async def add_consultation_view(
    request: Request,
    current_user: Optional[str] = Depends(get_current_user),
    token: Optional[str] = Query(None)
):
    # Try to get user from token in query params if not in header
    if not current_user and token:
        try:
            payload = decode_access_token(token)
            email: str = payload.get("sub")
            if email:
                current_user = email
        except Exception:
            pass
    
    # If still no user, return login page
    if not current_user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Please login to add consultation"
        })
    
    return templates.TemplateResponse("add_consultation.html", {
        "request": request
    })

@router.get("/consultation-dashboard", response_class=HTMLResponse)
async def consultation_dashboard_view(
    request: Request,
    current_user: Optional[str] = Depends(get_current_user),
    token: Optional[str] = Query(None)
):
    # Try to get user from token in query params if not in header
    if not current_user and token:
        try:
            payload = decode_access_token(token)
            email: str = payload.get("sub")
            if email:
                current_user = email
        except Exception:
            pass
    
    # If still no user, return login page
    if not current_user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Please login to view consultation dashboard"
        })
    
    return templates.TemplateResponse("consultation_dashboard.html", {
        "request": request
    })
