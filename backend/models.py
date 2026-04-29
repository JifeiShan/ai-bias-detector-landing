"""
数据库模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    plan = Column(String, default="free")  # free, pro, team
    created_at = Column(DateTime, default=datetime.utcnow)
    usage_count = Column(Integer, default=0)  # 使用次数


class DetectionRecord(Base):
    """检测记录表"""
    __tablename__ = "detection_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    input_text = Column(String, nullable=False)
    model = Column(String, default="gpt-3.5-turbo")
    bias_types = Column(JSON)  # ["gender", "race"]
    overall_score = Column(Float)
    bias_cases = Column(JSON)  # 详细案例
    recommendations = Column(JSON)  # 改进建议
    created_at = Column(DateTime, default=datetime.utcnow)


class Template(Base):
    """测试模板表"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    bias_type = Column(String, index=True)  # gender, race, age, occupation
    template_text = Column(String, nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)