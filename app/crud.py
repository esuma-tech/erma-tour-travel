from sqlalchemy.orm import Session
from sqlalchemy import select

from . import models, schemas


def list_tours(db: Session, featured_only: bool = False):
    stmt = select(models.Tour).order_by(models.Tour.created_at.desc())
    if featured_only:
        stmt = stmt.where(models.Tour.featured.is_(True))
    return db.scalars(stmt).all()


def get_tour(db: Session, tour_id: int):
    return db.get(models.Tour, tour_id)


def create_tour(db: Session, data: schemas.TourCreate):
    tour = models.Tour(**data.model_dump())
    db.add(tour)
    db.commit()
    db.refresh(tour)
    return tour


def create_booking(db: Session, data: schemas.BookingCreate):
    booking = models.Booking(**data.model_dump())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def create_inquiry(db: Session, data: schemas.InquiryCreate):
    inquiry = models.Inquiry(**data.model_dump())
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry


def list_bookings(db: Session):
    return db.scalars(select(models.Booking).order_by(models.Booking.created_at.desc())).all()


def list_inquiries(db: Session):
    return db.scalars(select(models.Inquiry).order_by(models.Inquiry.created_at.desc())).all()


def get_admin_by_username(db: Session, username: str):
    return db.scalar(select(models.AdminUser).where(models.AdminUser.username == username))


def create_admin(db: Session, username: str, password_hash: str):
    admin = models.AdminUser(username=username, password_hash=password_hash)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

