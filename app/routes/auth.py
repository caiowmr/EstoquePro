from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard.index'))
        
        flash('Usuário ou senha inválidos')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Rota para criar usuário inicial (apenas para o protótipo)
@auth_bp.route('/setup')
def setup():
    # Resetar banco de dados
    db.drop_all()
    db.create_all()
    
    # Criar admin
    admin = User(username='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Criar categorias e produtos de exemplo (Hardware de PC)
    from app.models import Produto, Funcionario, Movimentacao, Categoria
    
    categorias_data = [
        ('Processadores (CPU)', 'CPUs Intel e AMD'),
        ('Placas de Vídeo (GPU)', 'NVIDIA GeForce e AMD Radeon'),
        ('Memória RAM', 'Módulos DDR4 e DDR5'),
        ('Armazenamento', 'SSDs NVMe e HDDs'),
        ('Placas-Mãe', 'Motherboards AM4, AM5, LGA1700'),
        ('Fontes (PSU)', 'Power Supply Units 80 Plus'),
        ('Gabinetes', 'Cases ATX e ITX'),
        ('Coolers', 'Air e Water Coolers')
    ]
    
    categorias = []
    for nome, desc in categorias_data:
        cat = Categoria(nome=nome, descricao=desc)
        db.session.add(cat)
        categorias.append(cat)
    db.session.commit()

    produtos_data = [
        ('Intel Core i9-13900K', 'CPU-I9-13', 5, 15, 0),
        ('AMD Ryzen 7 7800X3D', 'CPU-R7-78', 8, 20, 0),
        ('NVIDIA RTX 4090 24GB', 'GPU-4090', 2, 5, 1),
        ('NVIDIA RTX 4070 Ti', 'GPU-4070T', 5, 12, 1),
        ('AMD Radeon RX 7900 XTX', 'GPU-7900X', 3, 8, 1),
        ('Corsair Vengeance 32GB DDR5', 'RAM-32-D5', 10, 45, 2),
        ('Kingston Fury 16GB DDR4', 'RAM-16-D4', 20, 60, 2),
        ('Samsung 990 Pro 2TB NVMe', 'SSD-990-2', 15, 30, 3),
        ('Crucial P3 1TB NVMe', 'SSD-P3-1', 25, 50, 3),
        ('ASUS ROG Strix Z790-E', 'MB-Z790-E', 4, 10, 4),
        ('MSI MAG B650 Tomahawk', 'MB-B650-T', 6, 18, 4),
        ('EVGA SuperNOVA 850G+', 'PSU-850G', 10, 25, 5),
        ('Corsair RM1000x', 'PSU-1000X', 5, 15, 5),
        ('Lian Li O11 Dynamic', 'CASE-O11D', 3, 12, 6),
        ('NZXT H7 Flow', 'CASE-H7F', 5, 15, 6),
        ('Noctua NH-D15', 'COOL-D15', 8, 20, 7),
        ('Corsair iCUE H150i', 'COOL-H150', 5, 12, 7),
        ('Intel Core i5-13600K', 'CPU-I5-13', 10, 25, 0),
        ('AMD Ryzen 5 7600X', 'CPU-R5-76', 12, 30, 0),
        ('NVIDIA RTX 4060 Ti', 'GPU-4060T', 15, 40, 1),
        ('G.Skill Trident Z5 32GB', 'RAM-32-G', 8, 22, 2),
        ('WD Black SN850X 1TB', 'SSD-SN850', 12, 28, 3),
        ('Gigabyte B550M Aorus Elite', 'MB-B550M', 20, 55, 4),
        ('Seasonic Focus GX-750', 'PSU-750W', 15, 35, 5),
        ('Be Quiet! Pure Base 500DX', 'CASE-500D', 6, 14, 6),
        ('DeepCool AK620', 'COOL-AK62', 15, 40, 7),
        ('AMD Ryzen 9 7950X', 'CPU-R9-79', 4, 10, 0),
        ('Intel Core i7-13700K', 'CPU-I7-13', 8, 18, 0),
        ('NVIDIA RTX 4080', 'GPU-4080', 3, 7, 1),
        ('TeamGroup T-Force 16GB', 'RAM-16-T', 25, 70, 2)
    ]
    
    produtos = []
    for nome, cod, min_e, atual, cat_idx in produtos_data:
        p = Produto(nome=nome, codigo=cod, estoque_minimo=min_e, estoque_atual=atual, categoria_id=categorias[cat_idx].id)
        db.session.add(p)
        produtos.append(p)
    
    funcionarios_nomes = [
        'Carlos Tech', 'Ana Hardware', 'Bruno Redes', 'Daniela Suporte', 
        'Eduardo Montagem', 'Fernanda Expedição', 'Gabriel Infra', 
        'Helena Manutenção', 'Igor Sistemas', 'Julia Qualidade'
    ]
    
    funcionarios = []
    for nome in funcionarios_nomes:
        f = Funcionario(nome=nome, departamento='TI')
        db.session.add(f)
        funcionarios.append(f)
    
    db.session.commit()

    # Adicionar muitas movimentações para os gráficos
    from datetime import datetime, timedelta
    import random
    
    # Gerar movimentações nos últimos 60 dias
    for i in range(60):
        data_mov = datetime.now() - timedelta(days=i)
        
        # Gerar entre 3 e 8 movimentações por dia
        for _ in range(random.randint(3, 8)):
            tipo = 'ENTRADA' if random.random() > 0.6 else 'SAIDA'
            p = random.choice(produtos)
            f = random.choice(funcionarios)
            
            m = Movimentacao(
                tipo=tipo, 
                quantidade=random.randint(1, 10), 
                produto_id=p.id, 
                funcionario_id=f.id,
                data=data_mov,
                observacao='Carga inicial de dados' if tipo == 'ENTRADA' else 'Atendimento de chamado'
            )
            db.session.add(m)
            
    db.session.commit()

    return "Sistema de Hardware configurado com 30 peças e 10 funcionários! Usuário: admin / Senha: admin123"
