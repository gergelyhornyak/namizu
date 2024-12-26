FROM python:3.9-slim-bullseye

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

RUN mkdir -p /app/logs

# Install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn

# Expose the port Flask will run on
EXPOSE 5000

# Set the command to run the app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
