from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Conexión al servidor de PostgreSQL (base por defecto: postgres)
engine = create_engine('postgresql://dbgame_sfhn_user:5UEkhDNGJaMQfAa5sNfHlZbPrFkoGCGF@dpg-d0llaopr0fns738g24og-a.oregon-postgres.render.com/dbgame_sfhn')

conn = engine.connect()
dbname = "dbgame_sfhn"

try:
    conn.execution_options(isolation_level="AUTOCOMMIT").execute(text(f"CREATE DATABASE {dbname}"))
    print(f"Base de datos '{dbname}' creada con éxito.")
except ProgrammingError:
    print(f"La base de datos '{dbname}' ya existe o hay un error.")
finally:
    conn.close()



