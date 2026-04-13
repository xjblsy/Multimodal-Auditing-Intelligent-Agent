from __future__ import annotations

import argparse
from pathlib import Path

from app.config import build_config
from app.importer import ImportManager, ImportOptions
from app.kb import KnowledgeBase
from app.server import run_server


def main() -> None:
    parser = argparse.ArgumentParser(description="Accounting audit smart coach")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("runserver", help="Run the local web application")
    subparsers.add_parser("rebuild", help="Rebuild the local knowledge index")

    ingest_parser = subparsers.add_parser("ingest", help="Import local files into the knowledge base")
    ingest_parser.add_argument("source", help="File or directory to import")
    ingest_parser.add_argument("--category", default="资料导入", help="Knowledge category")
    ingest_parser.add_argument("--industry", default="通用", help="Industry label")
    ingest_parser.add_argument("--tags", default="", help="Comma-separated tags")
    ingest_parser.add_argument("--difficulty", default="中级", help="Difficulty label")
    ingest_parser.add_argument(
        "--remote",
        action="store_true",
        help="Use DashScope document extraction for supported file types",
    )
    ingest_parser.add_argument(
        "--keep-remote-file",
        action="store_true",
        help="Keep uploaded files on DashScope instead of deleting them after extraction",
    )

    args = parser.parse_args()

    if args.command == "runserver":
        run_server()
        return

    if args.command == "rebuild":
        config = build_config()
        kb = KnowledgeBase(config)
        result = kb.rebuild_index()
        print(f"Rebuilt index: {result}")
        return

    if args.command == "ingest":
        config = build_config()
        kb = KnowledgeBase(config)
        manager = ImportManager(config, kb)
        source = Path(args.source)
        if not source.is_absolute():
            source = (config.root_dir / source).resolve()
        results = manager.ingest_path(
            source=source,
            options=ImportOptions(
                category=args.category,
                industry=args.industry,
                tags=[item.strip() for item in args.tags.split(",") if item.strip()],
                difficulty=args.difficulty,
                use_remote=args.remote,
                keep_remote_file=args.keep_remote_file,
            ),
        )
        print(f"Imported {len(results)} item(s):")
        for item in results:
            print(f"- {item['id']} | {item['title']} | {item['mode']} | {item['source']}")
        return


if __name__ == "__main__":
    main()
