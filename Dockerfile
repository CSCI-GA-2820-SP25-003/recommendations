FROM python:3.11-slim

# Working directory
WORKDIR /app
COPY . /app

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080

CMD ["python", "wsgi.py"]
