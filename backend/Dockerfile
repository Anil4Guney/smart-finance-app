FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

# Local development server. In production run: gunicorn config.wsgi:application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
