from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional, List

class UserCreate(BaseModel):
    name: str
    surename: str
    email: EmailStr
    phone_number: str
    password: str

class UserInDB(UserCreate):
    id: str
    creation_date: datetime = Field(default_factory=datetime.utcnow)

class Membership(BaseModel):
    user_id: str
    type: Literal["Testing", "Premium", "Tryout"]
    available: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class PatientCreate(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    second_last_name: Optional[str] = None
    address: str
    date_of_birth: datetime
    description: Optional[str] = None

class Patient(BaseModel):
    id: str
    user_id: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    second_last_name: Optional[str] = None
    address: str
    date_of_birth: datetime
    description: Optional[str] = None

class TempFile(BaseModel):
    file_id: str
    consultation_id: str
    user_id: str
    filename: str
    content_type: str
    file_data: bytes
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ConsultationCreate(BaseModel):
    patient_id: str
    date: datetime
    time: str
    description: str
    report_txt: str = ""
    resources: List[str] = []

class Consultation(BaseModel):
    consultation_id: str
    user_id: str
    patient_id: str
    date: datetime
    time: str
    description: str
    report_txt: str = ""
    resources: List[str] = []

