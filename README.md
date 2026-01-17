# Image Downloader

指定したWebページから全ての画像をダウンロードするPythonツール。

## 必要要件

- Python 3.11以上

## セットアップ

### 1. 仮想環境の作成

```bash
python -m venv .venv
```

### 2. 仮想環境の有効化

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.\.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python -m DownloadImagesOnPage <URL> <出力ディレクトリ> [オプション]
```

### オプション

- `--min-width <幅>`: 最小画像幅（ピクセル）
- `--min-height <高さ>`: 最小画像高さ（ピクセル）
- `--verbose`: 詳細な出力を表示
- `--help`: ヘルプメッセージを表示

### 使用例

```bash
# 基本的な使用
python -m DownloadImagesOnPage https://example.com ./images

# 最小サイズフィルタリング付き
python -m DownloadImagesOnPage https://example.com ./images --min-width 800 --min-height 600

# 詳細モード
python -m DownloadImagesOnPage https://example.com ./images --verbose
```

## テストの実行

```bash
pytest
```

カバレッジ付きでテストを実行:

```bash
pytest --cov=DownloadImagesOnPage --cov-report=html
```

## トラブルシューティング

- **`ModuleNotFoundError` / 依存関係が見つからない**: まず仮想環境が有効になっているか確認し、`pip install -r requirements.txt` を再実行してください。
- **PowerShellで有効化できない（実行ポリシー）**: 一時的に `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` を実行してから `.\.venv\Scripts\Activate.ps1` を実行してください。
- **URL取得に失敗する / 画像が0件になる**: 対象ページが動的生成（JavaScript）中心の可能性があります。本ツールは静的HTMLの `<img src="...">` のみ解析します。
- **一部画像が失敗する**: 404やタイムアウト等はスキップして継続します。`--verbose` を付けると詳細ログが確認できます。

## ライセンス

MIT License
