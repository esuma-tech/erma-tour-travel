from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field


class TourBase(BaseModel):
    title: str
    destination: str
    description: str
    duration_days: int = Field(ge=1)
    price_usd: float = Field(ge=0)
    image_url: str | None = None
    featured: bool = False


class TourCreate(TourBase):
    pass


class TourOut(TourBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    tour_id: int
    full_name: str
    email: str
    phone: str
    travelers: int = Field(ge=1, default=1)
    start_date: date
    notes: str | None = None


class BookingOut(BookingCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class InquiryCreate(BaseModel):
    full_name: str
    email: str
    phone: str | None = None
    subject: str
    message: str


class InquiryOut(InquiryCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
