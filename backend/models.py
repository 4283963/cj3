from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="名字")
    species = Column(String(50), nullable=False, comment="物种：猫/狗/其他")
    gender = Column(String(10), comment="性别")
    age = Column(String(50), comment="年龄")
    sterilized = Column(Boolean, default=False, comment="绝育状态")
    health_status = Column(String(200), comment="健康情况")
    found_location = Column(String(200), comment="发现地点")
    description = Column(Text, comment="描述")
    image_url = Column(String(500), comment="图片URL")
    status = Column(String(50), default="待领养", comment="状态：待领养/申请中/已领养")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    applications = relationship("AdoptionApplication", back_populates="animal")
    timelines = relationship("AnimalTimeline", back_populates="animal", cascade="all, delete-orphan")


class AdoptionApplication(Base):
    __tablename__ = "adoption_applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False, comment="动物ID")
    applicant_name = Column(String(100), nullable=False, comment="申请人姓名")
    applicant_phone = Column(String(20), nullable=False, comment="申请人电话")
    applicant_email = Column(String(100), comment="申请人邮箱")
    applicant_address = Column(String(500), comment="申请人住址")
    living_condition = Column(Text, comment="居住条件")
    experience = Column(Text, comment="养宠经验")
    reason = Column(Text, comment="领养原因")
    status = Column(String(50), default="待审核", comment="申请状态：待审核/已通过/已拒绝")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    animal = relationship("Animal", back_populates="applications")


class AnimalTimeline(Base):
    __tablename__ = "animal_timelines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False, comment="动物ID")
    author_name = Column(String(100), nullable=False, comment="发布人名字")
    content = Column(Text, nullable=False, comment="文字内容")
    image_url = Column(String(500), comment="图片URL")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    animal = relationship("Animal", back_populates="timelines")
    likes = relationship("AnimalTimelineLike", back_populates="timeline", cascade="all, delete-orphan")


class AnimalTimelineLike(Base):
    __tablename__ = "animal_timeline_likes"
    __table_args__ = (
        UniqueConstraint('timeline_id', 'visitor_id', name='uq_timeline_visitor'),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timeline_id = Column(Integer, ForeignKey("animal_timelines.id"), nullable=False, comment="动态ID")
    visitor_id = Column(String(100), nullable=False, comment="访客标识（匿名ID或用户名）")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    timeline = relationship("AnimalTimeline", back_populates="likes")
