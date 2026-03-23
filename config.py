import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-estoque-123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///estoque.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
