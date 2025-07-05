FROM python:3.12.3

# Create app dir
WORKDIR /app

# Copy requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY .env .
COPY token.json .
COPY src/ ./src

# Run it by default
CMD ["python", "src/main.py"]