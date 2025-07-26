#!/usr/bin/env python3
"""
Document ingestion script for Agno Vector DB.
Loads documents from various sources using Agno's built-in Knowledge classes.
"""

import argparse
import os
import time

from agno.document.chunking.semantic import SemanticChunking
from agno.embedder.google import GeminiEmbedder
from agno.knowledge.csv import CSVKnowledgeBase
from agno.knowledge.document import DocumentKnowledgeBase
from agno.vectordb.pgvector import PgVector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CHUNK_SIZE = 100


def setup_vector_db():
    """Setup pgvector database using Agno."""
    vector_db = PgVector(
        table_name=os.getenv("TABLE_NAME", "documents"),
        db_url=os.getenv("DATABASE_URL"),
        embedder=GeminiEmbedder(),  # or use the appropriate embeddings class
    )
    return vector_db


def load_text_knowledge(file_path: str, vector_db: PgVector):
    """Load text file knowledge using Agno's DocumentKnowledgeBase."""
    print(f"テキストファイルを処理中: {file_path}")

    try:
        # Create DocumentKnowledgeBase instance
        text_knowledge = DocumentKnowledgeBase(
            path=file_path,
            vector_db=vector_db,
            chunking_strategy=SemanticChunking(
                embedder=GeminiEmbedder(), chunk_size=CHUNK_SIZE
            ),
        )

        # Load the knowledge into vector database
        text_knowledge.load(upsert=True)
        print(f"テキストファイルの処理が完了しました: {file_path}")
        return True
    except Exception as e:
        print(f"テキストファイルの処理中にエラーが発生しました: {file_path}")
        print(f"エラー詳細: {e}")
        return False


def load_csv_knowledge(file_path: str, vector_db: PgVector):
    """Load CSV knowledge using Agno's CSVKnowledge."""
    print(f"CSVファイルを処理中: {file_path}")

    try:
        # Create CSV knowledge instance
        csv_knowledge = CSVKnowledgeBase(
            path=file_path,
            vector_db=vector_db,
            chunking_strategy=SemanticChunking(
                embedder=GeminiEmbedder(), chunk_size=CHUNK_SIZE
            ),
        )

        # Load the knowledge into vector database
        csv_knowledge.load(upsert=True)
        print(f"CSVファイルの処理が完了しました: {file_path}")
        return True
    except Exception as e:
        print(f"CSVファイルの処理中にエラーが発生しました: {file_path}")
        print(f"エラー詳細: {e}")
        return False


def clear_vector_db(vector_db: PgVector):
    """Clear all documents from the vector database."""
    print("データベースをクリアします...")
    try:
        vector_db.delete()
        print("データベースのクリアが完了しました。")
        return True
    except Exception as e:
        print(f"データベースのクリア中にエラーが発生しました: {e}")
        return False


def get_document_count(vector_db: PgVector) -> int:
    """Get the total number of documents in the vector database."""
    # Note: This method may need adjustment based on Agno API
    try:
        return len(vector_db.search("", limit=1000000))  # Rough count
    except Exception as e:
        print(f"Error getting document count: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into Agno Vector DB")
    parser.add_argument("--csv", help="CSV file to ingest")
    parser.add_argument("--text", help="Text file to ingest")

    parser.add_argument("--all", action="store_true", help="Ingest all sample data")
    parser.add_argument("--clear", action="store_true", help="Clear database")

    args = parser.parse_args()

    # Setup vector database
    vector_db = setup_vector_db()
    print("Agno Vector DBのセットアップが完了しました。")

    if args.clear:
        clear_vector_db(vector_db)
        return

    if args.all:
        success_count = 0
        total_operations = 0

        # Load CSV knowledge
        csv_path = "data/sample.csv"
        if os.path.exists(csv_path):
            total_operations += 1
            if load_csv_knowledge(csv_path, vector_db):
                success_count += 1
        else:
            print(f"CSVファイルが見つかりません: {csv_path}")

        time.sleep(10)

        # Load text knowledge
        text_path = "data/sample.txt"
        if os.path.exists(text_path):
            total_operations += 1
            if load_text_knowledge(text_path, vector_db):
                success_count += 1
        else:
            print(f"テキストファイルが見つかりません: {text_path}")

        # Show summary
        print("\n=== 処理結果サマリー ===")
        print(f"成功: {success_count}/{total_operations} 件")
        if success_count < total_operations:
            print(f"失敗: {total_operations - success_count} 件")
            print("注意: 一部の処理でエラーが発生しましたが、他の処理は継続されました")

        total_docs = get_document_count(vector_db)
        print(f"データベース内ドキュメント数: {total_docs} 件")

    elif args.csv:
        load_csv_knowledge(args.csv, vector_db)

    elif args.text:
        load_text_knowledge(args.text, vector_db)

    else:
        print("使用方法:")
        print(
            "  python ingest.py --all                    # 全サンプルデータを取り込み"
        )
        print("  python ingest.py --csv FILE               # CSVファイルを取り込み")
        print(
            "  python ingest.py --text FILE              # テキストファイルを取り込み"
        )
        print("  python ingest.py --clear                  # データベースクリア")


if __name__ == "__main__":
    main()
