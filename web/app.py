from pathlib import Path
import tempfile

from flask import Flask, render_template, request

from src.main import run


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = BASE_DIR / "data.json"

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    report = None
    error = None

    if request.method == "POST":
        uploaded_file = request.files.get("input_file")

        try:
            if uploaded_file and uploaded_file.filename:
                suffix = Path(uploaded_file.filename).suffix or ".json"

                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    suffix=suffix,
                    delete=False,
                ) as temp_file:
                    uploaded_file.save(temp_file)
                    input_path = Path(temp_file.name)

                try:
                    with tempfile.NamedTemporaryFile(
                        mode="w",
                        suffix=".json",
                        delete=False,
                    ) as output_file:
                        output_path = Path(output_file.name)

                    report = run(
                        input_path=str(input_path),
                        output_path=str(output_path),
                    )

                finally:
                    input_path.unlink(missing_ok=True)
                    output_path.unlink(missing_ok=True)

            else:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".json",
                    delete=False,
                ) as output_file:
                    output_path = Path(output_file.name)

                try:
                    report = run(
                        input_path=str(DEFAULT_INPUT),
                        output_path=str(output_path),
                    )
                finally:
                    output_path.unlink(missing_ok=True)

        except Exception as exc:
            error = str(exc)

    return render_template(
        "index.html",
        report=report,
        error=error,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)