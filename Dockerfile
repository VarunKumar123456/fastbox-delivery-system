# Minimal image - the simulator is stdlib-only, so this is a tiny, fast build.
FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Only needed for running the test suite inside the container; the
# simulator itself has no runtime dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Default: run the simulator against the bundled sample data and print the report.
CMD ["python", "-m", "src.main", "--input", "data.json", "--output", "report.json"]
