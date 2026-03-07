"""
OpenMemo REST Server.

Provides HTTP API access to OpenMemo.
Install with: pip install openmemo[server]

Usage:
    openmemo serve
    python -m openmemo.api.rest_server
"""

import json
import os

try:
    from flask import Flask, request, jsonify, make_response
    from flask_cors import CORS
except ImportError:
    raise ImportError("Install server dependencies: pip install openmemo[server]")

from openmemo.api.sdk import Memory
from openmemo.api.docs import API_DOCS_HTML
from openmemo.config import OpenMemoConfig


def create_app(db_path: str = None, config: OpenMemoConfig = None) -> Flask:
    app = Flask(__name__)
    CORS(app)

    db = db_path or os.environ.get("OPENMEMO_DB", "openmemo.db")
    from openmemo.storage.sqlite_store import SQLiteStore
    store = SQLiteStore(db_path=db, check_same_thread=False)
    memory = Memory(db_path=db, store=store, config=config)

    @app.route("/")
    def index():
        return jsonify({
            "service": "OpenMemo API",
            "version": "0.3.0",
            "description": "The Memory Infrastructure for AI Agents",
            "status": "running",
            "docs": "https://api.openmemo.ai/docs",
            "github": "https://github.com/openmemoai/openmemo",
            "endpoints": {
                "health": "GET /health",
                "write": "POST /memory/write",
                "recall": "POST /memory/recall",
                "search": "POST /memory/search",
                "scenes": "GET /memory/scenes",
                "delete": "DELETE /memory/{id}",
                "maintain": "POST /api/maintain",
                "stats": "GET /api/stats",
            },
        })

    @app.route("/docs")
    def docs():
        response = make_response(API_DOCS_HTML)
        response.headers["Content-Type"] = "text/html"
        return response

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "openmemo", "version": "0.3.0"})

    @app.route("/memory/write", methods=["POST"])
    @app.route("/api/memories", methods=["POST"])
    def write_memory():
        data = request.get_json()
        if not data or "content" not in data:
            return jsonify({"error": "content is required"}), 400

        memory_id = memory.add(
            content=data["content"],
            source=data.get("source", "api"),
            agent_id=data.get("agent_id", ""),
            scene=data.get("scene", ""),
            cell_type=data.get("cell_type", "fact"),
            metadata=data.get("metadata", {}),
        )
        return jsonify({"memory_id": memory_id}), 201

    @app.route("/memory/recall", methods=["POST"])
    @app.route("/api/memories/recall", methods=["POST"])
    def recall_memory():
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "query is required"}), 400

        results = memory.recall(
            query=data["query"],
            agent_id=data.get("agent_id", ""),
            scene=data.get("scene", ""),
            top_k=data.get("top_k", 10),
            budget=data.get("budget", 2000),
        )
        return jsonify({"results": results})

    @app.route("/memory/search", methods=["POST"])
    @app.route("/api/memories/search", methods=["POST"])
    def search_memory():
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "query is required"}), 400

        results = memory.search(
            query=data["query"],
            agent_id=data.get("agent_id", ""),
            top_k=data.get("top_k", 10),
        )
        return jsonify({"results": results})

    @app.route("/memory/reconstruct", methods=["POST"])
    @app.route("/api/memories/reconstruct", methods=["POST"])
    def reconstruct_memory():
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "query is required"}), 400

        result = memory.reconstruct(
            query=data["query"],
            agent_id=data.get("agent_id", ""),
            max_sources=data.get("max_sources", 10),
        )
        return jsonify(result)

    @app.route("/memory/scenes", methods=["GET"])
    def list_scenes():
        agent_id = request.args.get("agent_id", "")
        scenes = memory.scenes(agent_id=agent_id)
        return jsonify({"scenes": scenes})

    @app.route("/memory/<memory_id>", methods=["DELETE"])
    def delete_memory(memory_id):
        deleted = memory.delete(memory_id)
        if deleted:
            return jsonify({"deleted": True}), 200
        return jsonify({"error": "not found"}), 404

    @app.route("/api/maintain", methods=["POST"])
    def maintain():
        result = memory.maintain()
        return jsonify(result)

    @app.route("/api/stats")
    def stats():
        return jsonify(memory.stats())

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
