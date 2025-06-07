from sqlalchemy import Column, Integer, String, Float, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from models.base import engine

Base = declarative_base()

class Usuario(Base, UserMixin):
    __tablename__ = 'usuarios'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    full_name = Column(String(100), nullable=False)
    nationality = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)

class CancerData(Base):
    __tablename__ = 'cancer_data'
    patient_id = Column(String(50), primary_key=True, name='Patient_ID')  # Mapea a Patient_ID
    age = Column(Integer, nullable=True, name='Age')  # Mapea a Age
    gender = Column(String(50), nullable=False, name='Gender')  # Mapea a Gender
    region = Column(String(100), nullable=True, name='Country_Region')  # Mapea a Country_Region
    year = Column(Integer, nullable=True, name='Year')  # Mapea a Year
    genetic_risk = Column(Float, nullable=True, name='Genetic_Risk')  # Mapea a Genetic_Risk
    air_pollution = Column(Float, nullable=True, name='Air_Pollution')  # Mapea a Air_Pollution
    alcohol_consumption = Column(Float, nullable=True, name='Alcohol_Use')  # Mapea a Alcohol_Use
    smoking = Column(Float, nullable=True, name='Smoking')  # Mapea a Smoking
    obesity_level = Column(Float, nullable=True, name='Obesity_Level')  # Mapea a Obesity_Level
    cancer_type = Column(String(100), nullable=True, name='Cancer_Type')  # Mapea a Cancer_Type
    cancer_stage = Column(String(50), nullable=True, name='Cancer_Stage')  # Mapea a Cancer_Stage
    treatment_cost = Column(Float, nullable=True, name='Treatment_Cost_USD')  # Mapea a Treatment_Cost_USD
    survival_years = Column(Float, nullable=True, name='Survival_Years')  # Mapea a Survival_Years
    severity_score = Column(Float, nullable=True, name='Target_Severity_Score')  # Mapea a Target_Severity_Score

class ContactMessage(Base):
    __tablename__ = 'contact_messages'
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(120), nullable=False, index=True)
    message = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ContactMessage(id={self.id}, email='{self.email}')>"

Base.metadata.create_all(engine)