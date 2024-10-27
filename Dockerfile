# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the entire current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run your tests with the specified options
CMD ["sh", "-c", "PYTHONPATH=/app pytest -v -rf /app/tests/report_log.py --html-report=./report.html -p no:warnings"]