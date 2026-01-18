# Technology Stack

更新日: 2026-01-18

## Architecture

- **パイプライン型（オーケストレーション）**: `CLIConfig` を起点に、HTML取得 → 画像URL抽出 → ダウンロード → フィルタ → 保存 を直列で実行
- **レイヤ分割**: 上位（CLI/メイン/オーケストレータ）が下位（fetch/parse/download/filter/file I/O）を呼び出す。下位は上位に依存しない
- **例外階層でのエラー制御**: 取得/ダウンロード/書き込みをカスタム例外に集約して、終了コードとログで扱いを分ける

## Core Technologies

- **Language**: Python 3.11+
- **Packaging**: `pyproject.toml`（PEP 621）、`hatchling` ビルド
- **CLI**: `argparse`（標準ライブラリ）

## Key Libraries

- **requests**: HTML/画像のHTTP取得
- **beautifulsoup4 + lxml**: HTML解析と `img` 抽出
- **Pillow (PIL)**: 画像サイズ取得（フィルタリング）
- **playwright**: `--playwright` 時のレンダリング/画像キャプチャ

※依存の全列挙ではなく、開発パターンを左右する主要ライブラリのみを記録します。

## Development Standards

### Type Safety
- dataclass（`CLIConfig` / 結果モデル）と型ヒントを基本にする
- 共有データ構造は `models` に集約し、関数I/Oの型を明確にする

### Code Quality
- **Single-responsibility**: モジュールは責務を絞り、クロスカット（例外/モデル）は共有層へ
- **ログは `logging`**: `--verbose` で詳細化し、通常は要点のみ

### Testing
- `pytest` を中心に、CLI検証・ユニット・E2E/統合（Playwright含む）までカバー

## Development Environment

### Required Tools
- Python 3.11+
- `uv`（推奨）
- `--playwright` 利用時: Playwright のブラウザ（初回は `playwright install chromium`）

### Common Commands

```bash
# 開発環境セットアップ
uv sync --group dev

# 実行（ローカル）
uv run DownloadImagesOnPage <URL> <出力ディレクトリ>

# 動的ページ対応
uv run DownloadImagesOnPage <URL> <出力ディレクトリ> --playwright

# テスト
.venv\Scripts\python -m pytest
```

## Key Technical Decisions

- **CLIは `argparse` を採用**: 依存を増やさず、標準の挙動（help/exit）に乗る
- **画像単位で継続**: ダウンロード/保存の失敗は警告扱いで処理継続し、結果はサマリーで把握
- **ファイル衝突は回避**: 上書きではなくユニーク名生成で安全側に倒す
- **Playwrightモードは「描画結果」を保存**: ネットワークURLの直DLではなく、ページ上の `img` 要素をキャプチャする方針

---
_標準・パターン・重要な判断を記録し、依存の網羅は避ける_
