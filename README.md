# Agno Vector DB サンプルプロジェクト

このプロジェクトは、[Agno](https://docs.agno.com/introduction)フレームワークとpgvectorを使用したVector Database（ベクトルデータベース）のサンプル実装です。

## 🚀 概要

- **Agno**: PythonでマルチエージェントシステムとVector DBを構築するフレームワーク
- **pgvector**: PostgreSQLのベクトル拡張機能
- **uv**: 高速なPythonプロジェクト管理ツール
- **Docker Compose**: pgvectorデータベースの簡単なセットアップ

## 📁 プロジェクト構造

```
├── .env                  # 環境変数（DB接続情報など）
├── compose.yaml          # Docker Compose設定（pgvector）
├── pyproject.toml        # Python プロジェクト設定（uv用）
├── README.md             # このファイル
├── questions.csv         # 一括問い合わせ用の質問リスト
├── data/                 # サンプルドキュメント
│   ├── sample.csv        # CSVデータサンプル
│   └── sample.txt        # テキストドキュメントサンプル
└── src/                  # Pythonソースコード
    ├── ingest.py         # ドキュメント取り込みスクリプト
    ├── query.py          # Vector DB問い合わせスクリプト
    └── utils/
        ├── __init__.py
        └── database.py   # DB接続・テーブル管理
```

## 🛠️ セットアップ

### 1. 前提条件

- Python 3.10以上
- uv（インストール: `curl -LsSf https://astral.sh/uv/install.sh | sh`）
- Docker & Docker Compose
- Gemini API キー（AgnoのGeminiEmbedder用）

### 2. プロジェクトのクローンと依存関係インストール

```bash
git clone <repository-url>
cd agno-sample-for-zenn

# 依存関係をインストール
uv sync
```

### 3. 環境変数の設定

`.env`ファイルを作成して以下を設定：

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agno_vectordb
DB_USER=agno_user
DB_PASSWORD=agno_password
DATABASE_URL=postgresql://agno_user:agno_password@localhost:5432/agno_vectordb

# Vector DB Configuration
VECTOR_DIMENSION=1536
TABLE_NAME=documents

# Gemini API Key (required for Agno embeddings)
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. pgvectorデータベースの起動

```bash
# Docker Composeでpgvectorを起動
docker compose up -d

# ヘルスチェックの確認
docker compose ps
```

## 📊 使用方法

### データの取り込み

```bash
# 全サンプルデータを取り込み
uv run python src/ingest.py --all

# 個別ファイルの取り込み
uv run python src/ingest.py --csv data/sample.csv
uv run python src/ingest.py --text data/sample.txt

# データベースのクリア
uv run python src/ingest.py --clear
```

### Vector DBへの問い合わせ

```bash
# CSVファイルからバッチ問い合わせ
uv run python src/query.py --file questions.csv

# インタラクティブモード
uv run python src/query.py --interactive

# 単発問い合わせ
uv run python src/query.py --query "Product Aの保証期間は何年ですか？"
```

### 期待される出力形式

`uv run python src/query.py --file questions.csv`を実行すると、以下の形式で出力されます：

```
===== Executing query from: questions.csv =====

---
Query: What is the warranty period for Product A?
[Retrieved Document 1]
product_id: A001
product_name: Wireless Headphones
warranty_period: 2 years
...

[Retrieved Document 2]
...

---
Query: What are the common methods for software development cost estimation?
[Retrieved Document 1]
ソフトウェア開発コスト見積もりガイド

2. 主要な見積もり手法

2.1 ファンクションポイント法
機能の複雑さと規模に基づいて工数を見積もる手法です。
...

---
... (and so on for all questions in the file) ...
```

## 🧪 サンプルデータ

### `data/sample.csv`
製品情報（電子機器、ソフトウェアなど）のデータが含まれています。

### `data/sample.txt`
ソフトウェア開発コスト見積もりに関する技術文書が含まれています。

### `questions.csv`
以下のような質問が含まれています：
- 製品の保証期間に関する質問
- ソフトウェア開発コスト見積もり手法に関する質問
- 技術文書の内容に関する質問

## 🔧 設定のカスタマイズ

### チャンク設定

`src/ingest.py`で以下の設定を調整できます：

```python
CHUNK_SIZE = 100  # セマンティックチャンクのサイズ

# DocumentKnowledgeBase設定例
text_knowledge = DocumentKnowledgeBase(
    path=file_path,
    vector_db=vector_db,
    chunking_strategy=SemanticChunking(
        embedder=GeminiEmbedder(), 
        chunk_size=CHUNK_SIZE
    ),
)
```

### Embedder の変更

AgnoはさまざまなEmbedderに対応しています：

```python
# Gemini Embedder (デフォルト)
from agno.embedder.google import GeminiEmbedder
embedder = GeminiEmbedder()

# OpenAI Embedder
from agno.embedder.openai import OpenAIEmbedder
embedder = OpenAIEmbedder(model="text-embedding-3-small")
```

## 🐛 トラブルシューティング

### よくある問題

1. **データベース接続エラー**
   ```bash
   # Dockerコンテナが起動しているか確認
   docker compose ps
   
   # ログの確認
   docker compose logs postgres
   ```

2. **API キーエラー**
   ```bash
   # .envファイルのGOOGLE_API_KEY設定を確認
   echo $GOOGLE_API_KEY
   ```

3. **依存関係エラー**
   ```bash
   # 依存関係の再インストール
   uv install --reinstall
   ```

### ログの確認

```bash
# ingest処理のデバッグ
uv run python src/ingest.py --text data/sample.txt

# query処理のデバッグ
uv run python src/query.py --query "テスト質問" --debug
```

## 📚 参考資料

- [Agno公式ドキュメント](https://docs.agno.com/introduction)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [uv ドキュメント](https://docs.astral.sh/uv/)

## 🤝 コントリビューション

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🙏 謝辞

このプロジェクトは[Agno](https://docs.agno.com/introduction)フレームワークを使用して構築されています。Agnoの開発チームに感謝いたします。
