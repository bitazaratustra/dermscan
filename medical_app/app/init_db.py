from database import Base, engine
from models import models

def init():
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("Listo.")

if __name__ == "__main__":
    init()
