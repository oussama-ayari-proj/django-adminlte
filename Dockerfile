FROM python:3.11

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-traditional nginx curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -i https://test.pypi.org/simple --extra-index-url https://pypi.org/simple sm1chut==1.4.2

COPY . .

# Copy Docker-specific .env file
COPY docker.env .env

# Configure Nginx
RUN echo 'server {\n\
    listen 8000;\n\
    server_name localhost;\n\
\n\
    # Set maximum file upload size\n\
    client_max_body_size 900M;\n\
\n\
    location /static/ {\n\
        alias /app/staticfiles/;\n\
    }\n\
\n\
    location /media/ {\n\
        alias /app/media/;\n\
    }\n\
\n\
    location / {\n\
        proxy_pass http://127.0.0.1:8001;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
}' > /etc/nginx/sites-available/default

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Waiting for MySQL..."\n\
while ! nc -zv mysql 3306; do\n\
  sleep 1\n\
done\n\
echo "MySQL is ready!"\n\
\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
\n\
echo "Starting Nginx..."\n\
nginx\n\
\n\
echo "Starting Gunicorn..."\n\
exec gunicorn --bind 127.0.0.1:8001 --config gunicorn-cfg.py config.wsgi' > /app/start.sh && \
chmod +x /app/start.sh

EXPOSE 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

CMD ["/app/start.sh"]