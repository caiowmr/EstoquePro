# 📦 EstoquePro

Um sistema de gestão de estoque simples, direto e funcional — feito pra resolver o problema sem complicar.

A ideia aqui não é ser um ERP gigante, mas sim uma ferramenta prática pra controlar produtos, entradas, saídas e ter uma visão rápida do que tá acontecendo no estoque.

---

## 🚀 Rodando o projeto

Se você já mexeu com Python, vai ser tranquilo.

### Pré-requisitos

- Python 3.8+
- pip

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Rodar o sistema

```bash
python run.py
```

### 3. Primeira configuração

Na primeira vez, abre isso no navegador:

http://localhost:3000/setup

Isso vai:

- criar o banco
- gerar o usuário admin

**Login padrão:**

- usuário: `admin`
- senha: `admin123`

Depois é só acessar:

http://localhost:3000

---

## 🧠 O que o sistema faz

De forma simples:

- você cadastra **categorias**
- depois **produtos**
- e registra **entradas e saídas**

O sistema cuida do resto:

- atualiza o estoque automaticamente  
- registra quem fez cada movimentação  
- mostra tudo no dashboard  

---

## 📊 Dashboard

O dashboard é a parte mais útil:

- mostra o que mais saiu
- dá uma visão geral do estoque
- destaca produtos com pouco estoque

E o melhor:  
você pode reorganizar os widgets do jeito que quiser — e ele **lembra disso** (usa localStorage).

---

## ⚠️ Estoque crítico

Você pode definir um mínimo para cada produto.

Exemplo:

Produto X → mínimo: 10

Se cair pra 9, o sistema já marca como alerta.

Simples, mas resolve um problema real.

---

## 🛠 Tecnologias

### Backend

- Python + Flask  
- SQLAlchemy  
- SQLite  

Extras:

- Pandas / Openpyxl → exportar Excel  
- xhtml2pdf → gerar PDF  

### Frontend

- Bootstrap 5  
- Chart.js  
- GridStack.js (drag & drop no dashboard)  
- Lucide Icons  

---

## 📂 Estrutura do projeto

Nada muito mágico aqui, só organização:

EstoquePro/
├── app/
│   ├── models.py
│   ├── routes/
│   ├── services/
│   ├── static/
│   └── templates/
├── instance/
├── run.py
├── requirements.txt
└── metadata.json

Se você já viu Flask antes, vai se sentir em casa.

---

## 💡 Ideia por trás

Esse projeto foi pensado pra:

- ser rápido de rodar
- fácil de entender
- fácil de evoluir

Sem overengineering, sem mil camadas desnecessárias.

---

## 🧩 Possíveis melhorias (se quiser evoluir)

- autenticação mais robusta
- multiusuário com permissões
- banco PostgreSQL
- API REST
- deploy em nuvem
