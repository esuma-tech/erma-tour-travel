from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/api/tours", tags=["tours"])


@router.get("", response_model=list[schemas.TourOut])
def api_list_tours(featured: bool = False, db: Session = Depends(get_db)):
    return crud.list_tours(db, featured_only=featured)


@router.get("/{tour_id}", response_model=schemas.TourOut)
def api_get_tour(tour_id: int, db: Session = Depends(get_db)):
    tour = crud.get_tour(db, tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    return tour


@router.post("", response_model=schemas.TourOut, status_code=201)
def api_create_tour(data: schemas.TourCreate, db: Session = Depends(get_db)):
    return crud.create_tour(db, data)
