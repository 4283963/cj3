from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import get_db, init_db, USE_SQLITE
from models import Animal, AdoptionApplication
from schemas import (
    AnimalCreate,
    AnimalResponse,
    AnimalUpdate,
    ApplicationCreate,
    ApplicationResponse,
)

app = FastAPI(
    title="流浪猫狗救助领养系统",
    description="小区动物保护志愿者使用的流浪猫狗救助和领养管理系统",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_test_data(db: Session):
    existing = db.query(Animal).first()
    if existing:
        return

    test_animals = [
        Animal(
            name="橘宝",
            species="猫",
            gender="公",
            age="约2岁",
            sterilized=True,
            health_status="健康，已驱虫免疫",
            found_location="小区3号楼楼下",
            description="性格温顺，喜欢蹭人，会用猫砂盆。",
            image_url="",
            status="待领养"
        ),
        Animal(
            name="黑豆",
            species="狗",
            gender="公",
            age="约1岁",
            sterilized=False,
            health_status="健康，已打疫苗",
            found_location="小区北门花园",
            description="活泼好动，对人友好，会简单指令。",
            image_url="",
            status="待领养"
        ),
        Animal(
            name="小白",
            species="猫",
            gender="母",
            age="约6个月",
            sterilized=False,
            health_status="健康",
            found_location="小区5号楼地下室",
            description="胆小但很粘人，熟悉后会非常亲人。",
            image_url="",
            status="待领养"
        ),
        Animal(
            name="花花",
            species="猫",
            gender="母",
            age="约3岁",
            sterilized=True,
            health_status="健康，已绝育",
            found_location="小区垃圾站附近",
            description="性格独立，不喜欢被抱，但会安静地陪在你身边。",
            image_url="",
            status="待领养"
        ),
        Animal(
            name="大黄",
            species="狗",
            gender="公",
            age="约5岁",
            sterilized=True,
            health_status="健康，已绝育",
            found_location="小区停车场",
            description="性格沉稳，对小孩子很友善，适合有小孩的家庭。",
            image_url="",
            status="待领养"
        )
    ]

    db.add_all(test_animals)
    db.commit()
    print("✅ 测试数据初始化成功")


db_connected = init_db()
if db_connected and USE_SQLITE:
    from database import SessionLocal
    db = SessionLocal()
    try:
        init_test_data(db)
    finally:
        db.close()


@app.post("/api/vinit/animals", response_model=AnimalResponse, status_code=status.HTTP_201_CREATED)
def create_animal(animal: AnimalCreate, db: Session = Depends(get_db)):
    """
    录入动物档案
    """
    db_animal = Animal(**animal.model_dump())
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal


@app.post("/api/vinit/apply", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(application: ApplicationCreate, db: Session = Depends(get_db)):
    """
    提交领养申请，同时更新动物状态为"申请中"
    """
    animal = db.query(Animal).filter(Animal.id == application.animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {application.animal_id} 的动物不存在"
        )
    
    if animal.status == "已领养":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该动物已被领养，无法提交申请"
        )
    
    db_application = AdoptionApplication(**application.model_dump())
    db.add(db_application)
    
    animal.status = "申请中"
    
    db.commit()
    db.refresh(db_application)
    db.refresh(animal)
    
    return db_application


@app.get("/api/vinit/animals", response_model=List[AnimalResponse])
def get_animals(status: str = None, db: Session = Depends(get_db)):
    """
    获取动物列表，可按状态筛选
    """
    query = db.query(Animal)
    if status:
        query = query.filter(Animal.status == status)
    animals = query.order_by(Animal.created_at.desc()).all()
    return animals


@app.get("/api/vinit/animals/{animal_id}", response_model=AnimalResponse)
def get_animal(animal_id: int, db: Session = Depends(get_db)):
    """
    获取单个动物详情
    """
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {animal_id} 的动物不存在"
        )
    return animal


@app.patch("/api/vinit/animals/{animal_id}", response_model=AnimalResponse)
def update_animal(animal_id: int, animal_update: AnimalUpdate, db: Session = Depends(get_db)):
    """
    更新动物信息
    """
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {animal_id} 的动物不存在"
        )
    
    update_data = animal_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(animal, key, value)
    
    db.commit()
    db.refresh(animal)
    return animal


@app.get("/api/vinit/applications", response_model=List[ApplicationResponse])
def get_applications(db: Session = Depends(get_db)):
    """
    获取所有领养申请
    """
    applications = db.query(AdoptionApplication).order_by(AdoptionApplication.created_at.desc()).all()
    return applications


@app.get("/")
def root():
    return {
        "message": "流浪猫狗救助领养系统 API",
        "docs": "/docs",
        "database": "SQLite" if USE_SQLITE else "MySQL",
        "endpoints": {
            "POST /api/vinit/animals": "录入动物档案",
            "POST /api/vinit/apply": "提交领养申请",
            "GET /api/vinit/animals": "获取动物列表",
            "GET /api/vinit/animals/{id}": "获取动物详情",
            "PATCH /api/vinit/animals/{id}": "更新动物信息",
            "GET /api/vinit/applications": "获取领养申请列表",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
