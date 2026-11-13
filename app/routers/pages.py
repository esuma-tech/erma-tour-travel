from pathlib import Path
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud
from ..security import verify_password, create_session_token, read_session_token

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")
MEDIA_DIR = Path("app/static/media")

def list_media():
    if not MEDIA_DIR.exists():
        return [], []
    files = sorted([p.name for p in MEDIA_DIR.iter_files() if p.is_file()]) if False else []
    # correct iteration
    files = sorted([p.name for p in MEDIA_DIR.iterdir() if p.is_file()])
    images = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))]
    videos = [f for f in files if f.lower().endswith((".mp4", ".webm", ".mov"))]
    return images, videos

def current_admin(request: Request):
    token = request.cookies.get("admin_session")
    return read_session_token(token) if token else None

@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    featured = crud.list_tours(db, featured_only=True)
    tours = crud.list_tours(db)
    images, videos = list_media()
    return templates.TemplateResponse(request, "index.html", {"featured": featured, "tours": tours, "preview_images": images[:6]})

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
    return templates.TemplateResponse(request, "dashboard.html", {"images": images, "videos": videos, "tours": tours})

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

@router.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db)):
    user = current_admin(request)
    if not user:
        return RedirectResponse("/admin/login", status_code=303)
    return templates.TemplateResponse(request, "admin.html", {
        "user": user,
        "tours": crud.list_tours(db),
        "bookings": crud.list_bookings(db),
        "inquiries": crud.list_inquiries(db),
    })
