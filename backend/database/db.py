import psycopg2
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db_url="postgresql://postgres:varun%40123@localhost:5432/candidates"
engine=create_engine(db_url)
session=sessionmaker(autoflush=False,autocommit=False,bind=engine)
