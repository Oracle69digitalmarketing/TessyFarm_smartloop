# tessyfarm_smartloop/backend_api/app/apis/version1/endpoints/farm_management.py
from fastapi import APIRouter, HTTPException, Depends, Body, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ....core.db import get_db
from ....models.farm import Farm, Field, CropCycle # Import your SQLAlchemy models
from ..schemas import ( # Import your Pydantic schemas
    FarmCreate, FarmUpdate, FarmResponse, FarmResponseWithFields,
    FieldCreate, FieldUpdate, FieldResponse, FieldResponseWithCropCycles,
    CropCycleCreate, CropCycleUpdate, CropCycleResponse
)

router = APIRouter()

# --- Farm Endpoints ---

@router.post("/farms/", response_model=FarmResponse, status_code=status.HTTP_201_CREATED, tags=["Farm Management"])
def create_farm(farm: FarmCreate, db: Session = Depends(get_db)):
    db_farm = Farm(**farm.model_dump())
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    return db_farm

@router.get("/farms/", response_model=List[FarmResponse], tags=["Farm Management"])
def read_farms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    farms = db.query(Farm).offset(skip).limit(limit).all()
    return farms

@router.get("/farms/{farm_id}", response_model=FarmResponseWithFields, tags=["Farm Management"])
def read_farm(farm_id: int, db: Session = Depends(get_db)):
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if db_farm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    return db_farm # FastAPI will automatically use FarmResponseWithFields if fields relationship is loaded

@router.put("/farms/{farm_id}", response_model=FarmResponse, tags=["Farm Management"])
def update_farm(farm_id: int, farm_update: FarmUpdate, db: Session = Depends(get_db)):
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if db_farm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    
    update_data = farm_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_farm, key, value)
        
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    return db_farm

@router.delete("/farms/{farm_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Farm Management"])
def delete_farm(farm_id: int, db: Session = Depends(get_db)):
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if db_farm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    # Consider implications: what happens to fields and crop cycles?
    # For now, a simple delete. Production might need soft delete or checks for related entities.
    # if db_farm.fields: # Check if there are related fields
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete farm with associated fields. Delete fields first.")
    db.delete(db_farm)
    db.commit()
    return None # No content response

# --- Field Endpoints ---

@router.post("/fields/", response_model=FieldResponse, status_code=status.HTTP_201_CREATED, tags=["Field Management"])
def create_field(field: FieldCreate, db: Session = Depends(get_db)):
    # Check if farm_id exists
    db_farm = db.query(Farm).filter(Farm.id == field.farm_id).first()
    if not db_farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Farm with id {field.farm_id} not found")
    
    db_field = Field(**field.model_dump())
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field

@router.get("/fields/", response_model=List[FieldResponse], tags=["Field Management"])
def read_fields(farm_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Field)
    if farm_id is not None:
        query = query.filter(Field.farm_id == farm_id)
    fields = query.offset(skip).limit(limit).all()
    return fields

@router.get("/fields/{field_id}", response_model=FieldResponseWithCropCycles, tags=["Field Management"])
def read_field(field_id: int, db: Session = Depends(get_db)):
    db_field = db.query(Field).filter(Field.id == field_id).first()
    if db_field is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    return db_field

@router.put("/fields/{field_id}", response_model=FieldResponse, tags=["Field Management"])
def update_field(field_id: int, field_update: FieldUpdate, db: Session = Depends(get_db)):
    db_field = db.query(Field).filter(Field.id == field_id).first()
    if db_field is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")

    update_data = field_update.model_dump(exclude_unset=True)
    # If farm_id is being updated, check if the new farm_id exists
    if "farm_id" in update_data and update_data["farm_id"] is not None:
        db_farm = db.query(Farm).filter(Farm.id == update_data["farm_id"]).first()
        if not db_farm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Farm with id {update_data['farm_id']} not found")

    for key, value in update_data.items():
        setattr(db_field, key, value)
        
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field

@router.delete("/fields/{field_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Field Management"])
def delete_field(field_id: int, db: Session = Depends(get_db)):
    db_field = db.query(Field).filter(Field.id == field_id).first()
    if db_field is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    # if db_field.crop_cycles:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete field with associated crop cycles.")
    db.delete(db_field)
    db.commit()
    return None

# --- Crop Cycle Endpoints ---

@router.post("/crop-cycles/", response_model=CropCycleResponse, status_code=status.HTTP_201_CREATED, tags=["Crop Cycle Management"])
def create_crop_cycle(crop_cycle: CropCycleCreate, db: Session = Depends(get_db)):
    db_field = db.query(Field).filter(Field.id == crop_cycle.field_id).first()
    if not db_field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Field with id {crop_cycle.field_id} not found")
        
    db_crop_cycle = CropCycle(**crop_cycle.model_dump())
    db.add(db_crop_cycle)
    db.commit()
    db.refresh(db_crop_cycle)
    return db_crop_cycle

@router.get("/crop-cycles/", response_model=List[CropCycleResponse], tags=["Crop Cycle Management"])
def read_crop_cycles(field_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(CropCycle)
    if field_id is not None:
        query = query.filter(CropCycle.field_id == field_id)
    crop_cycles = query.offset(skip).limit(limit).all()
    return crop_cycles

@router.get("/crop-cycles/{cycle_id}", response_model=CropCycleResponse, tags=["Crop Cycle Management"])
def read_crop_cycle(cycle_id: int, db: Session = Depends(get_db)):
    db_crop_cycle = db.query(CropCycle).filter(CropCycle.id == cycle_id).first()
    if db_crop_cycle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop cycle not found")
    return db_crop_cycle

@router.put("/crop-cycles/{cycle_id}", response_model=CropCycleResponse, tags=["Crop Cycle Management"])
def update_crop_cycle(cycle_id: int, cycle_update: CropCycleUpdate, db: Session = Depends(get_db)):
    db_cycle = db.query(CropCycle).filter(CropCycle.id == cycle_id).first()
    if db_cycle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop cycle not found")

    update_data = cycle_update.model_dump(exclude_unset=True)
    if "field_id" in update_data and update_data["field_id"] is not None:
        db_field = db.query(Field).filter(Field.id == update_data["field_id"]).first()
        if not db_field:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Field with id {update_data['field_id']} not found")

    for key, value in update_data.items():
        setattr(db_cycle, key, value)
        
    db.add(db_cycle)
    db.commit()
    db.refresh(db_cycle)
    return db_cycle

@router.delete("/crop-cycles/{cycle_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Crop Cycle Management"])
def delete_crop_cycle(cycle_id: int, db: Session = Depends(get_db)):
    db_cycle = db.query(CropCycle).filter(CropCycle.id == cycle_id).first()
    if db_cycle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop cycle not found")
    # Consider if predictions are linked, etc.
    db.delete(db_cycle)
    db.commit()
    return None
