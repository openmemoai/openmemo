"""
OpenMemo CLI - Command line interface.

Usage:
    openmemo serve [--port PORT] [--db DB_PATH]
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="openmemo",
        description="OpenMemo - The Memory Infrastructure for AI Agents",
    )
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Start the OpenMemo API server")
    serve_parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8080)))
    serve_parser.add_argument("--host", type=str, default="0.0.0.0")
    serve_parser.add_argument("--db", type=str, default=os.environ.get("OPENMEMO_DB", "openmemo.db"))

    args = parser.parse_args()

    if args.command == "serve":
        try:
            from openmemo.api.rest_server import create_app
        except ImportError:
            print("Server dependencies not installed. Run: pip install openmemo[server]")
            sys.exit(1)

        app = create_app(db_path=args.db)
        print(f"OpenMemo API Server starting on {args.host}:{args.port}")
        print(f"Database: {args.db}")
        print(f"Docs: http://{args.host}:{args.port}/docs")
        app.run(host=args.host, port=args.port)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
