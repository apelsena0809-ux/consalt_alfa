FROM python:3.15-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip && python -m pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["sh", "-c", "python -m streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT}"]
