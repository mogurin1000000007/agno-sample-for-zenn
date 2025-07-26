#!/usr/bin/env python3
"""
Query script for Agno Vector DB.
Performs vector search on ingested documents using questions from CSV file.
"""

import argparse
import csv
import os
import time
from typing import List

from agno.embedder.google import GeminiEmbedder
from agno.vectordb.pgvector import PgVector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_vector_db():
    """Setup pgvector database using Agno."""
    vector_db = PgVector(
        table_name=os.getenv("TABLE_NAME", "documents"),
        db_url=os.getenv("DATABASE_URL"),
        embedder=GeminiEmbedder(),
    )
    return vector_db


def read_questions_from_csv(file_path: str) -> List[str]:
    """Read questions from CSV file."""
    questions = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if "question" in row:
                    questions.append(row["question"].strip())
        return questions
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {file_path}")
        return []
    except Exception as e:
        print(f"CSVファイル読み込みエラー: {e}")
        return []


def perform_search(vector_db: PgVector, query: str, limit: int = 1):
    """Perform vector search and return results."""
    try:
        results = vector_db.search(query=query, limit=limit)
        return results
    except Exception as e:
        print(f"検索エラー: {e}")
        return []


def format_search_results(query: str, results: List, query_index: int = None):
    """Format search results for display."""
    output = []
    if query_index is not None:
        output.append(f"Query {query_index}: {query}")
    else:
        output.append(f"Query: {query}")

    if not results:
        output.append("[検索結果が見つかりませんでした]")
    else:
        for i, result in enumerate(results, 1):
            # Agnoの検索結果の構造に応じて調整
            if hasattr(result, "document") and hasattr(result.document, "content"):
                content = result.document.content
            elif hasattr(result, "content"):
                content = result.content
            elif isinstance(result, dict):
                content = result.get("content", str(result))
            else:
                content = str(result)

            # 長すぎる場合は切り詰める
            if len(content) > 200:
                content = content[:200] + "..."

            output.append(f"[Retrieved Document {i}]")
            output.append(content)

    return output


def query_single_question(vector_db: PgVector, question: str):
    """Process a single question and display results."""
    print("---")
    results = perform_search(vector_db, question)
    formatted_output = format_search_results(question, results)

    for line in formatted_output:
        print(line)


def query_from_csv(vector_db: PgVector, csv_file: str):
    """Process all questions from CSV file."""
    print(f"===== Executing query from: {csv_file} =====")
    print()

    questions = read_questions_from_csv(csv_file)

    if not questions:
        print("質問が見つかりませんでした。")
        return

    for question in questions:
        if question:  # 空の質問をスキップ
            query_single_question(vector_db, question)
            time.sleep(5)

    print("---")
    print(f"\n処理完了: {len(questions)} 件の質問を処理しました。")


def interactive_query_mode(vector_db: PgVector):
    """Interactive query mode for manual queries."""
    print("インタラクティブクエリモード (終了するには 'quit' または 'exit' を入力)")
    print("=" * 50)

    while True:
        try:
            query = input("\n質問を入力してください: ").strip()

            if query.lower() in ["quit", "exit", "q"]:
                print("終了します。")
                break

            if not query:
                print("質問を入力してください。")
                continue

            print("\n検索中...")
            results = perform_search(vector_db, query)
            formatted_output = format_search_results(query, results)

            print("\n" + "=" * 50)
            for line in formatted_output:
                print(line)
            print("=" * 50)

        except KeyboardInterrupt:
            print("\n\n終了します。")
            break
        except Exception as e:
            print(f"エラーが発生しました: {e}")


def get_database_stats(vector_db: PgVector):
    """Get basic statistics about the database."""
    try:
        # 全てのドキュメントを取得してカウント（大まかな方法）
        all_results = vector_db.search("", limit=10000)  # 空クエリで全てを取得
        total_count = len(all_results)
        return total_count
    except Exception as e:
        print(f"統計情報取得エラー: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Query Agno Vector DB")
    parser.add_argument("--file", help="CSV file containing questions")
    parser.add_argument("--query", help="Single query to execute")
    parser.add_argument(
        "--interactive", action="store_true", help="Interactive query mode"
    )
    parser.add_argument("--stats", action="store_true", help="Show database statistics")

    args = parser.parse_args()

    # Setup vector database
    try:
        vector_db = setup_vector_db()
        print("Agno Vector DBに接続しました。")
    except Exception as e:
        print(f"データベース接続エラー: {e}")
        print("PostgreSQLコンテナが起動していることを確認してください。")
        return

    if args.stats:
        total_docs = get_database_stats(vector_db)
        print(f"データベース内ドキュメント数: {total_docs} 件")
        return

    if args.file:
        query_from_csv(vector_db, args.file)
    elif args.query:
        query_single_question(vector_db, args.query)
    elif args.interactive:
        interactive_query_mode(vector_db)
    else:
        print("使用方法:")
        print("  python query.py --file FILE              # CSVファイルからクエリ実行")
        print("  python query.py --query 'QUESTION'       # 単一クエリ実行")
        print("  python query.py --interactive            # インタラクティブモード")
        print("  python query.py --stats                  # データベース統計表示")


if __name__ == "__main__":
    main()
