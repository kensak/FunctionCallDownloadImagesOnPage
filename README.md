# Image Downloader

指定したWebページから全ての画像をダウンロードするPythonツール。

## 必要要件

- Python 3.11以上
- [uv](https://docs.astral.sh/uv/getting-started/installation/) （推奨）

## インストール

### uvを使用したインストール（推奨）

#### グローバルインストール

```bash
uv tool install download-images-on-page
```

インストール後、以下のコマンドで使用可能：

```bash
DownloadImagesOnPage <URL> <出力ディレクトリ> [オプション]
```

#### 一時実行（uvx）

インストール不要で即座に実行：

```bash
uvx --from download-images-on-page DownloadImagesOnPage <URL> <出力ディレクトリ> [オプション]
```

または
```bash
uv run DownloadImagesOnPage <URL> <出力ディレクトリ> [オプション]
```

### レガシー方式（venv + pip）

<details>
<summary>従来の仮想環境を使用する場合（クリックして展開）</summary>

1. 仮想環境の作成：
```bash
python -m venv .venv
```

2. 仮想環境の有効化：

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

3. 依存関係のインストール：
```bash
pip install -r requirements.txt
```

4. モジュールとして実行：
```bash
python -m DownloadImagesOnPage <URL> <出力ディレクトリ> [オプション]
```

</details>

## 使用方法

### コマンド形式

```bash
DownloadImagesOnPage <URL> <出力ディレクトリ> [オプション]
```

または、uvxで一時実行：

```bash
uvx --from download-images-on-page DownloadImagesOnPage <URL> <出力ディレクトリ> [オプション]
```

または、python -mで実行（後方互換性）：

```bash
python -m DownloadImagesOnPage <URL> <出力ディレクトリ> [オプション]
```

### オプション

- `--min-width <幅>`: 最小画像幅（ピクセル）
- `--min-height <高さ>`: 最小画像高さ（ピクセル）
- `--max-width <幅>`: 最大画像幅（ピクセル）
- `--max-height <高さ>`: 最大画像高さ（ピクセル）
- `--playwright`: JavaScriptレンダリングにPlaywrightを使用（動的コンテンツ対応）
- `--verbose`: 詳細な出力を表示
- `--help`: ヘルプメッセージを表示

### 使用例

```bash
# uv tool install後の基本的な使用
DownloadImagesOnPage https://example.com ./images

# uvxで一時実行
uvx --from download-images-on-page DownloadImagesOnPage https://example.com ./images

# JavaScriptで動的に生成される画像を含むページ（Playwrightを使用）
DownloadImagesOnPage https://example.com ./images --playwright

# 最小サイズフィルタリング付き
DownloadImagesOnPage https://example.com ./images --min-width 800 --min-height 600

# Playwrightと詳細モードの併用
DownloadImagesOnPage https://example.com ./images --playwright --verbose

# python -mでの実行（後方互換性）
python -m DownloadImagesOnPage https://example.com ./images
```

## Playwright機能

`--playwright`オプションを使用すると、Playwrightを使ってページをレンダリングしてから画像を抽出します。これにより以下のような利点があります：

- JavaScriptで動的に生成される画像を取得可能
- 遅延ロード（lazy loading）される画像に対応
- SPAやReactアプリなどのモダンなWebサイトに対応

**注意**: Playwrightを使用する場合、初回実行時にChromiumブラウザがダウンロードされます：

```bash
python -m playwright install chromium
```

## 開発環境のセットアップ

### uvを使用（推奨）

```bash
# リポジトリのクローン
git clone <repository-url>
cd FunctionCallDownloadImagesOnPage

# 開発依存関係を含む環境をセットアップ
uv sync --group dev

# テストの実行
.venv\Scripts\python -m pytest

# カバレッジ付きでテストを実行
.venv\Scripts\python -m pytest --cov=DownloadImagesOnPage --cov-report=html
```

### レガシー方式

<details>
<summary>venv + pipを使用する場合（クリックして展開）</summary>

```bash
# 仮想環境作成と有効化
python -m venv .venv
# (仮想環境を有効化 - 上記セットアップ手順参照)

# 依存関係インストール
pip install -r requirements.txt

# テスト実行（Windowsの場合）
.venv\Scripts\python -m pytest

# テスト実行（Linux/Macの場合）
.venv/bin/python -m pytest

# カバレッジ付き（Windows）
.venv\Scripts\python -m pytest --cov=DownloadImagesOnPage --cov-report=html

# カバレッジ付き（Linux/Mac）
.venv/bin/python -m pytest --cov=DownloadImagesOnPage --cov-report=html
```

</details>

## テストの実行

uv環境をセットアップ済みの場合：

```bash
.venv\Scripts\python -m pytest
```

または仮想環境を有効化している場合：

```bash
pytest
```

カバレッジ付きでテストを実行:

```bash
.venv\Scripts\python -m pytest --cov=DownloadImagesOnPage --cov-report=html
# または（仮想環境有効化時）
pytest --cov=DownloadImagesOnPage --cov-report=html
```

## トラブルシューティング

- **`ModuleNotFoundError` / 依存関係が見つからない**: まず仮想環境が有効になっているか確認し、`pip install -r requirements.txt` を再実行してください。
- **PowerShellで有効化できない（実行ポリシー）**: 一時的に `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` を実行してから `.\.venv\Scripts\Activate.ps1` を実行してください。
- **URL取得に失敗する / 画像が0件になる**: 対象ページが動的生成（JavaScript）中心の可能性があります。本ツールは静的HTMLの `<img src="...">` のみ解析します。
- **一部画像が失敗する**: 404やタイムアウト等はスキップして継続します。`--verbose` を付けると詳細ログが確認できます。

## ライセンス

MIT License
