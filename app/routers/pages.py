from pathlib import Path
from datetime import date
import shutil
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas
from ..security import (
    verify_password, create_session_token, read_session_token, hash_password,
    create_user_session_token, read_user_session_token,
)

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")
MEDIA_DIR = Path("app/static/media")


def list_media():
    if not MEDIA_DIR.exists():
        return [], []
    files = sorted([p.name for p in MEDIA_DIR.iterdir() if p.is_file()])
    images = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))]
    videos = [f for f in files if f.lower().endswith((".mp4", ".webm", ".mov"))]
    return images, videos


def current_admin(request: Request):
    token = request.cookies.get("admin_session")
    return read_session_token(token) if token else None


def current_user(request: Request, db: Session):
    token = request.cookies.get("user_session")
    uid = read_user_session_token(token) if token else None
    if not uid:
        return None
    return crud.get_user(db, uid)


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    featured = crud.list_tours(db, featured_only=True)
    tours = crud.list_tours(db)
    images, videos = list_media()
    posts = crud.list_dashboard_posts(db, published_only=True)[:6]
    return templates.TemplateResponse(request, "index.html", {"featured": featured, "tours": tours, "preview_images": images[:6], "posts": posts})


@router.get("/tours", response_class=HTMLResponse)
def tours_page(request: Request, db: Session = Depends(get_db)):
    tours = crud.list_tours(db)
    return templates.TemplateResponse(request, "tours.html", {"tours": tours})


@router.get("/tours/{tour_id}", response_class=HTMLResponse)
def tour_detail(request: Request, tour_id: int, db: Session = Depends(get_db)):
    tour = crud.get_tour(db, tour_id)
    return templates.TemplateResponse(request, "tour_detail.html", {"tour": tour})


@router.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(request, "about.html")


@router.get("/contact", response_class=HTMLResponse)
def contact(request: Request):
    return templates.TemplateResponse(request, "contact.html")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    images, videos = list_media()
    tours = crud.list_tours(db)
    posts = crud.list_dashboard_posts(db, published_only=True)
    return templates.TemplateResponse(request, "dashboard.html", {"images": images, "videos": videos, "tours": tours, "posts": posts})


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request, db: Session = Depends(get_db)):
    if current_user(request, db):
        return RedirectResponse("/book", status_code=303)
    return templates.TemplateResponse(request, "signup.html", {"error": None})


@router.post("/signup", response_class=HTMLResponse)
def signup(request: Request, full_name: str = Form(...), email: str = Form(...), phone: str = Form(""), password: str = Form(...), db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, email):
        return templates.TemplateResponse(request, "signup.html", {"error": "An account with this email already exists."}, status_code=400)
    user = crud.create_user(db, full_name, email, phone, hash_password(password))
    resp = RedirectResponse("/book?welcome=1", status_code=303)
    resp.set_cookie("user_session", create_user_session_token(user.id), httponly=True, samesite="lax")
    return resp


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    if current_user(request, db):
        return RedirectResponse("/book", status_code=303)
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login", response_class=HTMLResponse)
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request, "login.html", {"error": "Invalid email or password."}, status_code=401)
    resp = RedirectResponse("/book", status_code=303)
    resp.set_cookie("user_session", create_user_session_token(user.id), httponly=True, samesite="lax")
    return resp


@router.get("/logout")
def logout():
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie("user_session")
    return resp


@router.get("/book", response_class=HTMLResponse)
def book_page(request: Request, tour_id: int | None = None, db: Session = Depends(get_db)):
    user = current_user(request, db)
    tours = crud.list_tours(db)
    selected = tour_id
    success = request.query_params.get("success")
    welcome = request.query_params.get("welcome")
    my_bookings = []
    if user:
        # simple filter
        all_b = crud.list_bookings(db)
        my_bookings = [b for b in all_b if b.user_id == user.id]
    return templates.TemplateResponse(request, "book.html", {
        "user": user, "tours": tours, "selected_tour_id": selected,
        "success": success, "welcome": welcome, "my_bookings": my_bookings, "today": date.today().isoformat()
    })


@router.post("/book", response_class=HTMLResponse)
def book_submit(request: Request, tour_id: int = Form(...), full_name: str = Form(...), email: str = Form(...), phone: str = Form(...), travelers: int = Form(1), start_date: str = Form(...), notes: str = Form(""), db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/signup?next=book", status_code=303)
    if not crud.get_tour(db, tour_id):
        tours = crud.list_tours(db)
        return templates.TemplateResponse(request, "book.html", {"user": user, "tours": tours, "selected_tour_id": tour_id, "success": None, "welcome": None, "my_bookings": [], "today": date.today().isoformat(), "error": "Selected tour not found."}, status_code=400)
    booking_data = schemas.BookingCreate(tour_id=tour_id, full_name=full_name, email=email, phone=phone, travelers=travelers, start_date=date.fromisoformat(start_date), notes=notes or None)
    crud.create_booking(db, booking_data, user_id=user.id)
    return RedirectResponse("/book?success=1", status_code=303)


@router.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    if current_admin(request):
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(request, "admin_login.html", {"error": None})


@router.post("/admin/login", response_class=HTMLResponse)
def admin_login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    admin = crud.get_admin_by_username(db, username)
    if not admin or not verify_password(password, admin.password_hash):
        return templates.TemplateResponse(request, "admin_login.html", {"error": "Invalid username or password"}, status_code=401)
    resp = RedirectResponse("/admin", status_code=303)
    resp.set_cookie("admin_session", create_session_token(admin.username), httponly=True, samesite="lax")
    return resp


@router.get("/admin/logout")
def admin_logout():
    resp = RedirectResponse("/admin/login", status_code=303)
    resp.delete_cookie("admin_session")
    return resp


def require_admin(request: Request):
    user = current_admin(request)
    return user


@router.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, edit_tour: int | None = None, db: Session = Depends(get_db)):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/admin/login", status_code=303)
    images, videos = list_media()
    media_files = ["/static/media/" + f for f in images + videos]
    tours = crud.list_tours(db)
    selected_tour = crud.get_tour(db, edit_tour) if edit_tour else None
    return templates.TemplateResponse(request, "admin.html", {
        "user": user,
        "tours": tours,
        "bookings": crud.list_bookings(db),
        "inquiries": crud.list_inquiries(db),
        "posts": crud.list_dashboard_posts(db),
        "media_files": media_files,
        "images": images,
        "videos": videos,
        "notice": request.query_params.get("notice"),
        "edit_tour": selected_tour,
        "edit_tour_id": edit_tour,
    })


@router.post("/admin/tours/create")
def admin_create_tour(request: Request, title: str = Form(...), destination: str = Form(...), description: str = Form(...), duration_days: int = Form(...), price_usd: float = Form(...), image_url: str = Form(""), featured: str = Form(""), db: Session = Depends(get_db)):
    if not require_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    crud.create_tour(db, {"title": title, "destination": destination, "description": description, "duration_days": duration_days, "price_usd": price_usd, "image_url": image_url or None, "featured": featured == "on"})
    return RedirectResponse("/admin?notice=tour_created", status_code=303)


@router.post("/admin/tours/{tour_id}/update")
def admin_update_tour(request: Request, tour_id: int, title: str = Form(...), destination: str = Form(...), description: str = Form(...), duration_days: int = Form(...), price_usd: float = Form(...), image_url: str = Form(""), featured: str = Form(""), db: Session = Depends(get_db)):
    if not require_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    crud.update_tour(db, tour_id, {"title": title, "destination": destination, "description": description, "duration_days": duration_days, "price_usd": price_usd, "image_url": image_url or None, "featured": featured == "on"})
    return RedirectResponse("/admin?notice=tour_updated", status_code=303)


@router.post("/admin/tours/{tour_id}/delete")
def admin_delete_tour(request: Request, tour_id: int, db: Session = Depends(get_db)):
    if not require_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    crud.delete_tour(db, tour_id)
    return RedirectResponse("/admin?notice=tour_deleted", status_code=303)


@router.post("/admin/posts/create")
def admin_create_post(request: Request, title: str = Form(...), body: str = Form(""), media_url: str = Form(""), media_type: str = Form("image"), sort_order: int = Form(0), is_published: str = Form(""), db: Session = Depends(get_db)):
    if not require_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    crud.create_dashboard_post(db, {"title": title, "body": body or None, "media_url": media_url or None, "media_type": media_type, "sort_order": sort_order, "is_published": is_published == "on"})
    return RedirectResponse("/admin?notice=post_created", status_code=303)


@router.post("/admin/posts/{post_id}/update")
def admin_update_post(request: Request, post_id: int, title: str = Form(...), body: str = Form(""), media_url: str = Form(""), media_type: str = Form("image"), sort_order: int = Form(0), is_published: str = Form(""), db: Session = Depends(get_db)):
    if not require_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    crud.update_dashboard_post(db, post_id, {"title": title, "body": body or None, "media_url": media_url or None, "media_type": media_type, "sort_order": sort_order, "is_published": is_published == "on"})
    return RedirectResponse("/admin?notice=post_updated", status_code=303)


@router.post("/admin/posts/{post_id}/delete")
def admin_delete_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    if not require_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    crud.delete_dashboard_post(db, post_id)
    return RedirectResponse("/admin?notice=post_deleted", status_code=303)


@router.post("/admin/media/upload")
async def admin_upload_media(request: Request, files: list[UploadFile] = File(...)):
    if not require_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    allowed = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".webm", ".mov"}
    saved = 0
    for f in files:
        if not f.filename:
            continue
        name = Path(f.filename).name
        suffix = Path(name).suffix.lower()
        if suffix not in allowed:
            continue
        dest = MEDIA_DIR / name
        if dest.exists():
            stem, suf = dest.stem, dest.suffix
            i = 1
            while dest.exists():
                dest = MEDIA_DIR / f"{stem}_{i}{suf}"
                i += 1
        with dest.open("wb") as out:
            shutil.copyfileobj(f.file, out)
        saved += 1
    return RedirectResponse(f"/admin?notice=uploaded_{saved}", status_code=303)


@router.post("/admin/media/delete")
def admin_delete_media(request: Request, filename: str = Form(...)):
    if not require_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    name = Path(filename).name
    target = (MEDIA_DIR / name).resolve()
    if MEDIA_DIR.resolve() in target.parents or target.parent == MEDIA_DIR.resolve():
        if target.exists() and target.is_file():
            target.unlink()
    return RedirectResponse("/admin?notice=media_deleted", status_code=303)
