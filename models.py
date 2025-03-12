from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5432/mydatabase"

# Création du moteur de connexion
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Création du modèle de base
Base = declarative_base()

# Définition du modèle Titanic
class Titanic(Base):
    __tablename__ = "titanic"
    
    passenger_id = Column(Integer, primary_key=True)
    pclass = Column(Integer)
    name = Column(String)
    sex = Column(String)
    age = Column(Float, nullable=True)
    sibsp = Column(Integer)
    parch = Column(Integer)
    ticket = Column(String)
    fare = Column(Float)
    cabin = Column(String, nullable=True)
    embarked = Column(String)
    
# Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer les tables dans la base de données
Base.metadata.create_all(bind=engine)
