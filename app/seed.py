from sqlalchemy import select, func
from .database import SessionLocal
from . import models
from .security import hash_password


def seed_if_empty():
    db = SessionLocal()
    try:
        count = db.scalar(select(func.count()).select_from(models.Tour)) or 0
        if count == 0:
            tours = [
                models.Tour(title="Historic Lalibela", destination="Lalibela, Amhara", description="Explore the rock-hewn churches of Lalibela, a UNESCO World Heritage site and spiritual heart of Ethiopia.", duration_days=4, price_usd=650, featured=True, image_url="https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=1200"),
                models.Tour(title="Simien Mountains Trek", destination="Simien Mountains, Amhara", description="Trek dramatic escarpments, spot gelada baboons and the Ethiopian wolf in one of Africa's most stunning landscapes.", duration_days=6, price_usd=980, featured=True, image_url="https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=1200"),
                models.Tour(title="Danakil Depression Adventure", destination="Afar Region", description="Witness Erta Ale lava lake, colorful sulfur springs of Dallol, and vast salt flats in one of the hottest places on Earth.", duration_days=5, price_usd=1100, featured=True, image_url="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1200"),
                models.Tour(title="Omo Valley Cultural Journey", destination="Omo Valley, SNNPR", description="Immerse yourself in the living traditions of the diverse tribes of the Omo Valley with respectful, guided visits.", duration_days=7, price_usd=1250, featured=False, image_url="https://images.unsplash.com/photo-1523805009345-7448845a9e53?w=1200"),
                models.Tour(title="Addis Ababa City & Heritage", destination="Addis Ababa", description="Discover the National Museum, Holy Trinity Cathedral, Merkato, and the vibrant culinary scene of Ethiopia's capital.", duration_days=2, price_usd=220, featured=False, image_url="https://images.unsplash.com/photo-1618828665011-0abd973f7bb8?w=1200"),
                models.Tour(title="Bale Mountains & Wildlife", destination="Bale Mountains, Oromia", description="Track the rare Ethiopian wolf on the Sanetti Plateau and walk through the lush Harenna Forest.", duration_days=5, price_usd=890, featured=False, image_url="https://images.unsplash.com/photo-1549366021-9f761d450615?w=1200"),
            ]
            db.add_all(tours)

        admin = db.scalar(select(models.AdminUser).where(models.AdminUser.username == "erma"))
        if not admin:
            db.add(models.AdminUser(username="erma", password_hash=hash_password("ebm@123")))

        db.commit()
    finally:
        db.close()

