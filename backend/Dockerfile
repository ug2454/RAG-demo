# RAG FastAPI Backend Dockerfile
FROM python:3.10-slim
WORKDIR /app
# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
# Copy app code
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
