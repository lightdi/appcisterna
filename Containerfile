FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
EXPOSE 5000
EXPOSE 1883
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "3"]