FROM python:3.10-slim

WORKDIR /app

# Install FFmpeg and dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean
    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py",  "--server.runOnSave=true", "--server.headless=true", "--server.port=8501", "--server.address=0.0.0.0"]
