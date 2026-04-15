FROM python:3.11-slim

# Installer les dépendances système nécessaires à mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier requirements.txt et installer les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du projet
COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
