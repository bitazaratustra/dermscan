from pydantic import BaseModel, EmailStr

class DoctorBase(BaseModel):
    email: EmailStr
    full_name: str

class DoctorCreate(DoctorBase):
    password: str
    license_number: str
    specialty: str | None = None
    hospital_affiliation: str | None = None

class DoctorResponse(DoctorBase):
    id: int
    specialty: str | None
    license_number: str
    hospital_affiliation: str | None

    class Config:
        orm_mode = True

class DoctorLogin(BaseModel):
    email: EmailStr
    password: str
