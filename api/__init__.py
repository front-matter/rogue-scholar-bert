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
from quart_rate_limiter import RateLimiter, RateLimit
from quart_cors import cors

from api.inference import classify

config = Config()
config.from_toml("hypercorn.toml")
load_dotenv()
rate_limiter = RateLimiter()
logger = logging.getLogger(__name__)
version = "0.2.0"

app = Quart(__name__, static_folder="static", static_url_path="")
app.config.from_prefixed_env()
QuartSchema(app, info=Info(title="Rogue Scholar Bert API", version=version))
rate_limiter = RateLimiter(app, default_limits=[RateLimit(15, timedelta(seconds=60))])
app = cors(app, allow_origin="*")


def run() -> None:
    """Run the app."""
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    import asyncio
    
    config = Config()
    config.bind = ["0.0.0.0:5100"]
    
    asyncio.run(serve(app, config))


@app.route("/heartbeat")
async def heartbeat():
    """Heartbeat."""
    return "OK", 200


@app.route("/classify", methods=["POST"])
async def classify_text():
    """classify text input."""
    if (
        request.headers.get("Authorization", None) is None
        or request.headers.get("Authorization").split(" ")[1]
        != environ["QUART_SERVICE_KEY"]
    ):
        return {"error": "Unauthorized."}, 401

    title = request.args.get("title", None)
    abstract = request.args.get("abstract", None)
    if not title and not abstract:
        return {"error": "No input provided"}, 400

    result = await classify(title, abstract)
    return jsonify(result)
