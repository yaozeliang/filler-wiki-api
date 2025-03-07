FROM python:3.10-slim

WORKDIR /app

# Install PDM
RUN pip install pdm

# Copy PDM files
COPY pyproject.toml pdm.lock* ./

# Install dependencies
RUN pdm install --prod --no-lock --no-editable

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run the application
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT 