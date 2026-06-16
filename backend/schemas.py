from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AnimalBase(BaseModel):
    name: str = Field(..., description="名字", max_length=100)
    species: str = Field(..., description="物种：猫/狗/其他", max_length=50)
    gender: Optional[str] = Field(None, description="性别", max_length=10)
    age: Optional[str] = Field(None, description="年龄", max_length=50)
    sterilized: bool = Field(False, description="绝育状态")
    health_status: Optional[str] = Field(None, description="健康情况", max_length=200)
    found_location: Optional[str] = Field(None, description="发现地点", max_length=200)
    description: Optional[str] = Field(None, description="描述")
    image_url: Optional[str] = Field(None, description="图片URL", max_length=500)


class AnimalCreate(AnimalBase):
    pass


class AnimalUpdate(BaseModel):
    name: Optional[str] = Field(None, description="名字", max_length=100)
    species: Optional[str] = Field(None, description="物种", max_length=50)
    gender: Optional[str] = Field(None, description="性别", max_length=10)
    age: Optional[str] = Field(None, description="年龄", max_length=50)
    sterilized: Optional[bool] = Field(None, description="绝育状态")
    health_status: Optional[str] = Field(None, description="健康情况", max_length=200)
    found_location: Optional[str] = Field(None, description="发现地点", max_length=200)
    description: Optional[str] = Field(None, description="描述")
    image_url: Optional[str] = Field(None, description="图片URL", max_length=500)
    status: Optional[str] = Field(None, description="状态", max_length=50)


class AnimalResponse(AnimalBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationBase(BaseModel):
    animal_id: int = Field(..., description="动物ID")
    applicant_name: str = Field(..., description="申请人姓名", max_length=100)
    applicant_phone: str = Field(..., description="申请人电话", max_length=20)
    applicant_email: Optional[str] = Field(None, description="申请人邮箱", max_length=100)
    applicant_address: Optional[str] = Field(None, description="申请人住址", max_length=500)
    living_condition: Optional[str] = Field(None, description="居住条件")
    experience: Optional[str] = Field(None, description="养宠经验")
    reason: Optional[str] = Field(None, description="领养原因")


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationReview(BaseModel):
    status: str = Field(..., description="审核结果：已通过/已拒绝")
    remark: Optional[str] = Field(None, description="审核备注", max_length=500)


class ApplicationResponse(ApplicationBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimelineCreate(BaseModel):
    author_name: str = Field(..., description="发布人名字", max_length=100)
    content: str = Field(..., description="文字内容")
    image_url: Optional[str] = Field(None, description="图片URL", max_length=500)


class TimelineResponse(BaseModel):
    id: int
    animal_id: int
    author_name: str
    content: str
    image_url: Optional[str] = None
    like_count: int = 0
    liked_by_me: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnimalDetailResponse(AnimalResponse):
    timelines: List[TimelineResponse] = []


class LikeToggle(BaseModel):
    visitor_id: str = Field(..., description="访客标识", max_length=100)
