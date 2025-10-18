FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cach-dir -r requirements.txt gunicorn
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "3"]
