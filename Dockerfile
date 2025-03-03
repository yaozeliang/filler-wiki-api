FROM python:3.10-slim

WORKDIR /app

# Install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# Copy only dependency files first
COPY pyproject.toml README.md ./

# Install dependencies
RUN pdm install --prod --no-lock --no-editable

# Copy the rest of the application
COPY app app/

# Expose port
EXPOSE 8000

# Run the application
CMD ["pdm", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 