from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.produtos import produtos_bp
    from app.routes.movimentacoes import mov_bp
    from app.routes.relatorios import relatorios_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(mov_bp)
    app.register_blueprint(relatorios_bp)

    with app.app_context():
        db.create_all()

    from app.routes.categorias import categorias_bp
    from app.routes.funcionarios import funcionarios_bp
    app.register_blueprint(categorias_bp)
    app.register_blueprint(funcionarios_bp)
    
    return app
