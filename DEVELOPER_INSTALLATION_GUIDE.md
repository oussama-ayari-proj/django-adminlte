# 🚀 Guide d'Installation pour Développeurs - Système de Gestion Hospitalière

<style>
table {
  border-collapse: collapse;
  width: 100%;
  margin: 20px 0;
}

table, th, td {
  border: 1px solid black;
}

th, td {
  padding: 12px 15px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
  font-weight: bold;
}

tr:nth-child(even) {
  background-color: #f9f9f9;
}

tr:hover {
  background-color: #f5f5f5;
}

code {
  background-color: #f4f4f4;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

pre {
  background-color: #f4f4f4;
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
}
</style>

## 📋 Vue d'ensemble

Ce guide détaille l'installation et la configuration complète du système de gestion hospitalière Django AdminLTE pour les développeurs.

---

## 🛠️ Prérequis Système

### Configuration Minimale Requise

| Composant | Version Minimale | Version Recommandée | Notes |
|-----------|------------------|---------------------|--------|
| **Python** | 3.9+ | 3.11+ | Avec pip et venv |
| **Node.js** | 16+ | 18+ LTS | Pour les dépendances frontend |
| **Base de données** | MySQL 8.0+ | MySQL 8.0+ | SQLite pour développement |
| **RAM** | 4 GB | 8 GB+ | Pour les calculs ML |
| **Stockage** | 10 GB | 20 GB+ | Espace libre |

### Outils de Développement

| Outil | Description | Installation |
|-------|-------------|-------------|
| **Git** | Contrôle de version | `winget install Git.Git` (Windows) |
| **VS Code** | Éditeur recommandé | `winget install Microsoft.VisualStudioCode` |
| **MySQL** | Base de données | `winget install Oracle.MySQL` |

---

## 📥 Installation Étape par Étape

### 🚀 Option Recommandée : Docker Compose (Développement Rapide)

#### Installation complète avec données de test
```bash
# Cloner le repository
git clone https://github.com/oussama-ayari-proj/django-adminlte.git
cd django-adminlte
# IMPORTANT !! Décompresse le backup.rar avant cette commande !!!! en backup.sql
# Lancer l'environnement complet avec Docker
docker-compose up --build
```

#### Vérification de l'installation Docker
- **Interface principale** : http://localhost:8000
- **Interface admin** : http://localhost:8000/admin
- **Base de données MySQL** : localhost:3306 (root/password)

---

### 🔧 Option Alternative : Installation Manuelle

### 1. 🔄 Clonage du Projet

```bash
# Cloner le repository
git clone https://github.com/oussama-ayari-proj/django-adminlte.git
cd django-adminlte

# Vérifier la branche active
git branch
```

### 2. 🐍 Configuration Python

#### Création de l'environnement virtuel
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### Installation des dépendances Python
```bash
# Mise à jour de pip
python -m pip install --upgrade pip

# Installation des dépendances
pip install -r requirements.txt

# Installation du client MySQL pour Python
pip install mysqlclient

# Vérification de l'installation
pip list
```

### 3. 🗄️ Configuration de la Base de Données

#### Option A : Utilisation du backup.sql (Recommandé pour développement)
```bash
# Se connecter à MySQL
mysql -u root -p

# Créer la base de données
CREATE DATABASE hospital_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Importer les données de test depuis backup.sql
mysql -u root -p hospital_management < backup.sql
```


#### Option B : SQLite (Développement simple)
```bash
# SQLite est utilisé par défaut pour le développement
# Aucune configuration supplémentaire nécessaire
```

### 4. ⚙️ Configuration de l'Application

#### Fichier de configuration environnement
```bash
# Copier le fichier d'exemple
cp env.sample .env

# Éditer les variables d'environnement
# Windows
notepad .env

# Linux/macOS
nano .env
ou
vim .env
```

#### Variables d'environnement essentielles
```bash
# .env
DEBUG=True
SECRET_KEY=your-very-secret-key-here
# Pour MySQL
DATABASE_URL=mysql://hospital_user:your_password@localhost:3306/hospital_management

# Pour SQLite (développement)
# DATABASE_URL=sqlite:///db.sqlite3


```

### 5. 🔄 Migrations de Base de Données

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```


### 6. 🏃‍♂️ Lancement du Serveur

#### Serveur de développement Django
```bash
# Lancer le serveur
python manage.py runserver

# Avec un port spécifique
python manage.py runserver 8080

# Pour accès réseau
python manage.py runserver 0.0.0.0:8000
```

#### Vérification de l'installation
- **Interface principale** : http://localhost:8000
- **Interface admin** : http://localhost:8000/admin
- **API Documentation** : http://localhost:8000/api/docs (si configuré)

---

## 🔧 Configuration Avancée

### Machine Learning et Prédictions

#### Installation des dépendances ML
```bash
# Dépendances ML spécifiques
pip install scikit-learn==1.3.0
pip install pandas numpy matplotlib seaborn
pip install mlflow


```

#### Configuration MLflow
```bash
# Lancer le serveur MLflow
mlflow server --host 127.0.0.1 --port 5000

# Interface MLflow : http://localhost:5000
```

### Configuration Nginx (Production)

#### Fichier de configuration Nginx
```nginx
# /etc/nginx/sites-available/hospital-management
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/django-adminlte/static/;
    }

    location /media/ {
        alias /path/to/django-adminlte/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🐳 Installation avec Docker

### Dockerfile de développement
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

#### Installation des dépendances système
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# Port d'exposition
EXPOSE 8000

# Commande par défaut
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Docker Compose
```yaml
# docker-compose.yml
services:
  optisoin-app:
    image: oussamaayari2020/optisoin-app:2.3.2
    container_name: optisoin
    restart: always
    ports: 
      - "8000:8000"
    depends_on:
      - mysql
    networks:
      - app_network
  mlflow:
    image: oussamaayari2020/mlflow-deployment:1.0.0
    container_name: mlflow
    restart: always
    ports:
      - "5000:5000"
    networks:
      - app_network
  mysql:
    image: mysql:8.0
    container_name: mysql-server
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: mydb
      MYSQL_USER: user
      MYSQL_PASSWORD: userpass
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./backup.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app_network
volumes:
  mysql_data:

networks:
  app_network:
    driver: bridge
```

### Commandes Docker
```bash


# Lancer en arrière-plan
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

---

## 🧪 Configuration de Développement


## 🔍 Dépannage

### Problèmes Courants

| Problème | Solution |
|----------|----------|
| **ModuleNotFoundError** | Vérifier l'activation de l'environnement virtuel |
| **Database connection error** | Vérifier les credentials MySQL dans .env |
| **Port already in use** | Changer le port ou tuer le processus existant |
| **Static files not found** | Exécuter `python manage.py collectstatic` |
| **Permission denied** | Vérifier les permissions des fichiers et dossiers |
| **mysqlclient installation error** | Installer les dev tools: `apt-get install default-libmysqlclient-dev` (Linux) |




## 📚 Ressources Additionnelles

### Documentation
- **Django** : https://docs.djangoproject.com/
- **AdminLTE** : https://adminlte.io/docs/
- **Chart.js** : https://www.chartjs.org/docs/
- **Select2** : https://select2.org/

### Outils de Développement
- **Django Extensions** : https://django-extensions.readthedocs.io/
- **Django Debug Toolbar** : https://django-debug-toolbar.readthedocs.io/
- **Django REST Framework** : https://www.django-rest-framework.org/



---

*Guide d'installation mis à jour le 28 juillet 2025*
