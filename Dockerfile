# FastBox web demo
FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Start the recruiter-facing web application.
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "web.app:app"]