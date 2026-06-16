from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from typing import List
import logging

from database import get_db, init_db, USE_SQLITE
from models import Animal, AdoptionApplication
from schemas import (
    AnimalCreate,
    AnimalResponse,
    AnimalUpdate,
    ApplicationCreate,
    ApplicationResponse,
    ApplicationReview,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
    增加并发控制：行级锁 + 事务 + 状态二次校验
    """
    try:
        animal_id = application.animal_id

        if USE_SQLITE:
            db.execute(text("BEGIN IMMEDIATE"))
            animal = db.query(Animal).filter(Animal.id == animal_id).first()
        else:
            animal = db.query(Animal).filter(Animal.id == animal_id).with_for_update().first()

        if not animal:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID 为 {animal_id} 的动物不存在"
            )

        current_status = animal.status
        logger.info(f"动物 {animal_id} ({animal.name}) 当前状态: {current_status}")

        if current_status != "待领养":
            db.rollback()
            if current_status == "申请中":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="该动物已有领养申请正在审核中，无法重复申请"
                )
            elif current_status == "已领养":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该动物已被领养，无法提交申请"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"该动物当前状态为「{current_status}」，无法提交领养申请"
                )

        db_application = AdoptionApplication(**application.model_dump())
        db.add(db_application)
        db.flush()

        animal.status = "申请中"
        db.flush()

        if not USE_SQLITE:
            db.refresh(animal)
            if animal.status != "申请中":
                db.rollback()
                logger.error(f"动物 {animal_id} 状态更新失败，预期: 申请中, 实际: {animal.status}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="动物状态更新失败，请稍后重试"
                )

        pending_count = db.query(func.count(AdoptionApplication.id)).filter(
            AdoptionApplication.animal_id == animal_id,
            AdoptionApplication.status == "待审核"
        ).scalar()

        if pending_count > 1:
            db.rollback()
            logger.warning(f"检测到动物 {animal_id} 存在 {pending_count} 个待审核申请，回滚当前申请")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该动物已有领养申请正在处理中，请稍后再试"
            )

        db.commit()
        db.refresh(db_application)
        db.refresh(animal)

        logger.info(f"领养申请提交成功: 申请ID={db_application.id}, 动物ID={animal_id}, 动物状态={animal.status}")

        return db_application

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"提交领养申请时发生异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交申请失败: {str(e)}"
        )


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


@app.patch("/api/vinit/applications/{application_id}/review", response_model=ApplicationResponse)
def review_application(
    application_id: int,
    review: ApplicationReview,
    db: Session = Depends(get_db)
):
    """
    审核领养申请，通过时自动更新动物状态为"已领养"，并拒绝其他待审核申请
    增加并发控制：行级锁 + 事务 + 状态校验
    """
    try:
        if review.status not in ["已通过", "已拒绝"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="审核状态只能是「已通过」或「已拒绝」"
            )

        if USE_SQLITE:
            db.execute(text("BEGIN IMMEDIATE"))
            application = db.query(AdoptionApplication).filter(
                AdoptionApplication.id == application_id
            ).first()
        else:
            application = db.query(AdoptionApplication).filter(
                AdoptionApplication.id == application_id
            ).with_for_update().first()

        if not application:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID 为 {application_id} 的申请不存在"
            )

        if application.status != "待审核":
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该申请当前状态为「{application.status}」，无法重复审核"
            )

        animal_id = application.animal_id

        if USE_SQLITE:
            animal = db.query(Animal).filter(Animal.id == animal_id).first()
        else:
            animal = db.query(Animal).filter(Animal.id == animal_id).with_for_update().first()

        if not animal:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID 为 {animal_id} 的动物不存在"
            )

        logger.info(f"审核申请 {application_id}: 动物={animal.name}({animal_id}), 当前状态={animal.status}, 审核结果={review.status}")

        if review.status == "已通过":
            if animal.status != "申请中":
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"动物当前状态为「{animal.status}」，无法通过领养申请"
                )

            application.status = "已通过"
            animal.status = "已领养"
            db.flush()

            if not USE_SQLITE:
                db.refresh(animal)
                if animal.status != "已领养":
                    db.rollback()
                    logger.error(f"动物 {animal_id} 状态更新失败，预期: 已领养, 实际: {animal.status}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="动物状态更新失败，请稍后重试"
                    )

            other_pending = db.query(AdoptionApplication).filter(
                AdoptionApplication.animal_id == animal_id,
                AdoptionApplication.id != application_id,
                AdoptionApplication.status == "待审核"
            ).all()

            for other_app in other_pending:
                other_app.status = "已拒绝"
                logger.info(f"自动拒绝申请 {other_app.id}: 因申请 {application_id} 已通过")

            db.flush()

            approved_count = db.query(func.count(AdoptionApplication.id)).filter(
                AdoptionApplication.animal_id == animal_id,
                AdoptionApplication.status == "已通过"
            ).scalar()

            if approved_count > 1:
                db.rollback()
                logger.error(f"检测到动物 {animal_id} 存在 {approved_count} 个已通过申请，回滚审核操作")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="检测到并发冲突，该动物已有其他申请通过审核，请刷新后重试"
                )

        else:
            application.status = "已拒绝"
            db.flush()

            pending_count = db.query(func.count(AdoptionApplication.id)).filter(
                AdoptionApplication.animal_id == animal_id,
                AdoptionApplication.status == "待审核"
            ).scalar()

            if pending_count == 0:
                animal.status = "待领养"
                logger.info(f"动物 {animal_id} 所有申请已拒绝，状态恢复为「待领养」")
                db.flush()

        db.commit()
        db.refresh(application)
        db.refresh(animal)

        logger.info(f"申请 {application_id} 审核完成: 状态={application.status}, 动物状态={animal.status}")

        return application

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"审核申请时发生异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"审核失败: {str(e)}"
        )


@app.get("/")
def root():
    return {
        "message": "流浪猫狗救助领养系统 API",
        "docs": "/docs",
        "database": "SQLite" if USE_SQLITE else "MySQL",
        "features": "已启用并发控制：行级锁 + 事务 + 状态二次校验",
        "endpoints": {
            "POST /api/vinit/animals": "录入动物档案",
            "POST /api/vinit/apply": "提交领养申请（并发安全）",
            "GET /api/vinit/animals": "获取动物列表",
            "GET /api/vinit/animals/{id}": "获取动物详情",
            "PATCH /api/vinit/animals/{id}": "更新动物信息",
            "GET /api/vinit/applications": "获取领养申请列表",
            "PATCH /api/vinit/applications/{id}/review": "审核领养申请（并发安全）",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
