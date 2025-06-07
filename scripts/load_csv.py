import pandas as pd
from sqlalchemy import create_engine
import os
import sys
# Agrega el path al directorio raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.model import Base, cancer_data
from sqlalchemy.orm import sessionmaker

# Configura tu conexión
DATABASE_URL = "postgresql://postgres:123456@localhost:5432/cancer_data"  # ← cámbialo

# Crear engine y sesión
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Crear tablas si no existen
Base.metadata.create_all(engine)

# Leer el CSV con pandas
CSV_URL = "https://raw.githubusercontent.com/rudyluis/DashboardJS/refs/heads/main/global_cancer.csv"
df = pd.read_csv(CSV_URL)

# Limpieza / transformación si es necesario

# Convertir DataFrame en lista de objetos VideoGameSale
records = [
    cancer_data(
        Patient_ID=row['Patient_ID'],
        Age=row['Age'],
        Gender=row['Gender'],
        Country_Region=row['Country_Region'],
        Year=row['Year'],
        Genetic_Risk=row['Genetic_Risk'],
        Air_Pollution=row['Air_Pollution'],
        Alcohol_Use=row['Alcohol_Use'],
        Smoking=row['Smoking'],
        Obesity_Level=row['Obesity_Level'],
        Cancer_Type=row['Cancer_Type'],
        Cancer_Stage=row['Cancer_Stage'],
        Treatment_Cost_USD=row['Treatment_Cost_USD'],
        Survival_Years=row['Survival_Years'],
        Target_Severity_Score=row['Target_Severity_Score']
    )
    for index, row in df.iterrows()
]

# Insertar en la base de datos
session.bulk_save_objects(records)
session.commit()
print("✅ Migración de datos completada")
session.close()