# Use a slim python 3.9 image as the base
FROM python:3.9-slim

# Set a working directory for the application
WORKDIR /app

# Copy requirements.txt file
COPY requirements.txt .

# Install dependencies using pip
RUN pip install -r requirements.txt

# Copy your application code
COPY . .

# Expose the port the application will run on
EXPOSE 30678

# Command to run the application
CMD [ "python3", "bankpy/bank.py" ]
