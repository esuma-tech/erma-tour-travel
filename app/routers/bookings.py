from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/api", tags=["bookings"])


@router.post("/bookings", response_model=schemas.BookingOut, status_code=201)
def api_create_booking(data: schemas.BookingCreate, db: Session = Depends(get_db)):
    if not crud.get_tour(db, data.tour_id):
        raise HTTPException(status_code=404, detail="Tour not found")
    return crud.create_booking(db, data)


@router.post("/inquiries", response_model=schemas.InquiryOut, status_code=201)
def api_create_inquiry(data: schemas.InquiryCreate, db: Session = Depends(get_db)):
    return crud.create_inquiry(db, data)
