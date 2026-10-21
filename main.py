"""Flask API for Karma Mining.

``GET /combined/<post_id>`` is the route the UI uses. It fetches the thread
once, scores each top-level comment with the context analyzer and the
Bayesian ridge model, and returns ``int(context * regression)`` sorted
high to low. Post id ``demo`` skips Reddit and scores a slice of the
bundled sample file.
"""

import json
import os
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS
from prawcore.exceptions import PrawcoreException

from contextual import contextual
from regressor import regressor

DEMO_POST_ID = "demo"
DEMO_COMMENT_LIMIT = 12
DEFAULT_DATA = Path(__file__).resolve().parent / "data" / "sample_comments.jsonl"


def load_comment_bodies(path, limit=None):
    bodies = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            bodies.append(json.loads(line)["body"])
            if limit is not None and len(bodies) >= limit:
                break
    return bodies


def json_safe(score):
    if hasattr(score, "item"):
        score = score.item()
    if isinstance(score, float):
        return float(score)
    return int(score)


def ranked_comments(score_map):
    ordered = sorted(
        score_map.items(),
        key=lambda item: (item[1], item[0]),
        reverse=True,
    )
    return [{"comment": text, "score": json_safe(score)} for text, score in ordered]


def combine_scores(context_scores, regression_scores):
    """Preserve the 2018 formula, including truncation toward zero."""
    combined = {}
    for text, context_score in context_scores.items():
        combined[text] = int(context_score * regression_scores[text])
    return combined


def create_app(context_model=None, regression_model=None, data_file=None):
    app = Flask(__name__)
    CORS(app)
    data_path = Path(data_file or os.environ.get("DATA_FILE", DEFAULT_DATA))

    if context_model is None:
        context_model = contextual()
    if regression_model is None:
        if not data_path.is_file():
            raise FileNotFoundError(
                f"Training file not found: {data_path}. The original comment "
                "dump was not part of this repo. Use data/sample_comments.jsonl "
                "or set DATA_FILE to a JSONL file of {body, score} rows."
            )
        regression_model = regressor(data_path)

    def comments_for(post_id):
        if post_id == DEMO_POST_ID:
            return load_comment_bodies(data_path, limit=DEMO_COMMENT_LIMIT)
        return context_model.fetch_comments(post_id)

    def respond(build):
        try:
            return jsonify(build())
        except (RuntimeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400
        except FileNotFoundError as exc:
            return jsonify({"error": str(exc)}), 500
        except PrawcoreException as exc:
            return jsonify({"error": f"Reddit request failed: {exc}"}), 502

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/context_analyze/<post_id>")
    def only_context(post_id):
        app.logger.info("context_analyze %s", post_id)

        def build():
            return ranked_comments(context_model.score(comments_for(post_id)))

        return respond(build)

    @app.get("/regressor1/<post_id>")
    def only_regressor(post_id):
        app.logger.info("regressor1 %s", post_id)

        def build():
            return ranked_comments(regression_model.score(comments_for(post_id)))

        return respond(build)

    @app.get("/combined/<post_id>")
    def combined(post_id):
        app.logger.info("combined %s", post_id)

        def build():
            comments = comments_for(post_id)
            context_scores = context_model.score(comments)
            regression_scores = regression_model.score(comments)
            return ranked_comments(combine_scores(context_scores, regression_scores))

        return respond(build)

    return app


if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get("PORT", "8080"))
    application.run(host="0.0.0.0", port=port)
