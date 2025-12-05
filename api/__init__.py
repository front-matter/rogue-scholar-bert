"""Main quart application"""

from hypercorn.config import Config
import logging
from datetime import timedelta
from os import environ
from dotenv import load_dotenv
from quart import Quart, request, jsonify
from quart_schema import (
    QuartSchema,
    Info,
)
from quart_rate_limiter import RateLimiter, rate_limit
from quart_cors import cors

from api.inference import classify

config = Config()
config.from_toml("hypercorn.toml")
load_dotenv()
logger = logging.getLogger(__name__)
version = "0.2.1"

app = Quart(__name__, static_folder="static", static_url_path="")
app.config.from_prefixed_env()
QuartSchema(app, info=Info(title="Rogue Scholar Bert API", version=version))
rate_limiter = RateLimiter(app)
app = cors(app, allow_origin="*")


def run() -> None:
    """Run the app."""
    app.run(host="0.0.0.0", port=5100)


@app.route("/heartbeat")
async def heartbeat():
    """Heartbeat."""
    return "OK", 200


@app.route("/classify", methods=["POST"])
@rate_limit(8, timedelta(seconds=10))
async def classify_text():
    """classify text input."""
    if (
        request.headers.get("Authorization", None) is None
        or request.headers.get("Authorization").split(" ")[1]
        != environ["QUART_SERVICE_KEY"]
    ):
        return {"error": "Unauthorized."}, 401

    data = await request.get_json()
    if not data:
        return {"error": "No JSON data provided"}, 400

    result = await classify(data.get("title", None), data.get("abstract", None))
    return jsonify(result)


@app.errorhandler(429)
async def ratelimit_handler(e):
    retry_after = getattr(e, "retry_after", None)
    if retry_after and hasattr(retry_after, "total_seconds"):
        retry_seconds = int(retry_after.total_seconds())
    else:
        retry_seconds = 30
    return (
        jsonify(
            {
                "error": "Too Many Requests",
                "detail": "Rate limit exceeded. Please retry later.",
            }
        ),
        429,
        {"retry-after": str(retry_seconds)},
    )
