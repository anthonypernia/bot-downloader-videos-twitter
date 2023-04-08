FROM python:3.7
RUN pip install --upgrade pip
# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
# Copy source code except for the .dockerignore files
COPY . .
# Run the app
CMD ["python", "runner.py"]
