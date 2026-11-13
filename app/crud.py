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


def create_tour(db: Session, data):
    if isinstance(data, schemas.TourCreate):
        payload = data.model_dump()
    else:
        payload = data
    tour = models.Tour(**payload)
    db.add(tour)
    db.commit()
    db.refresh(tour)
    return tour


def update_tour(db: Session, tour_id: int, data: dict):
    tour = db.get(models.Tour, tour_id)
    if not tour:
        return None
    for k, v in data.items():
        if hasattr(tour, k):
            setattr(tour, k, v)
    db.commit()
    db.refresh(tour)
    return tour


def delete_tour(db: Session, tour_id: int):
    tour = db.get(models.Tour, tour_id)
    if not tour:
        return False
    db.delete(tour)
    db.commit()
    return True


def create_booking(db: Session, data, user_id: int | None = None):
    payload = data.model_dump() if hasattr(data, "model_dump") else data
    booking = models.Booking(**payload, user_id=user_id)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def list_bookings(db: Session):
    return db.scalars(select(models.Booking).order_by(models.Booking.created_at.desc())).all()


def create_inquiry(db: Session, data):
    payload = data.model_dump() if hasattr(data, "model_dump") else data
    inquiry = models.Inquiry(**payload)
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry


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


def get_user_by_email(db: Session, email: str):
    return db.scalar(select(models.User).where(models.User.email == email.lower().strip()))


def get_user(db: Session, user_id: int):
    return db.get(models.User, user_id)


def create_user(db: Session, full_name: str, email: str, phone: str | None, password_hash: str):
    user = models.User(
        full_name=full_name.strip(),
        email=email.lower().strip(),
        phone=(phone or "").strip() or None,
        password_hash=password_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_dashboard_posts(db: Session, published_only: bool = False):
    stmt = select(models.DashboardPost).order_by(models.DashboardPost.sort_order.asc(), models.DashboardPost.created_at.desc())
    if published_only:
        stmt = stmt.where(models.DashboardPost.is_published.is_(True))
    return db.scalars(stmt).all()


def get_dashboard_post(db: Session, post_id: int):
    return db.get(models.DashboardPost, post_id)


def create_dashboard_post(db: Session, data: dict):
    post = models.DashboardPost(**data)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_dashboard_post(db: Session, post_id: int, data: dict):
    post = db.get(models.DashboardPost, post_id)
    if not post:
        return None
    for k, v in data.items():
        if hasattr(post, k):
            setattr(post, k, v)
    db.commit()
    db.refresh(post)
    return post


def delete_dashboard_post(db: Session, post_id: int):
    post = db.get(models.DashboardPost, post_id)
    if not post:
        return False
    db.delete(post)
    db.commit()
    return True


def get_setting(db: Session, key: str, default: str = ""):
    row = db.get(models.SiteSetting, key)
    return row.value if row else default


def set_setting(db: Session, key: str, value: str):
    row = db.get(models.SiteSetting, key)
    if row:
        row.value = value
    else:
        db.add(models.SiteSetting(key=key, value=value))
    db.commit()
    return row or db.get(models.SiteSetting, key)
