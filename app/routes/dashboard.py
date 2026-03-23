from flask import Blueprint, render_template, request
from flask_login import login_required
from app.services.dashboard_service import DashboardService

dashboard_bp = Blueprint('dashboard', __name__)

from datetime import datetime

@dashboard_bp.route('/')
@login_required
def index():
    periodo = request.args.get('periodo', 'semana')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    inicio, fim = DashboardService._get_periodo_dates(periodo, start_date, end_date)
    
    resumo = DashboardService.get_resumo_cards(inicio, fim)
    graficos = DashboardService.get_dados_graficos(inicio, fim)
    return render_template('dashboard.html', resumo=resumo, graficos=graficos, periodo=periodo, start_date=start_date, end_date=end_date, now=datetime.now())
