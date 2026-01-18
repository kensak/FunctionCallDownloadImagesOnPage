# Project Structure

更新日: 2026-01-18

## Organization Philosophy

- **小さなモジュールに責務分離**し、オーケストレータがフローを組み立てる構成
- 共有概念（設定/結果/例外）は「共有層」に寄せ、機能モジュール間の依存を減らす
- 追加機能は「既存の流れに差し込める小さな関数」として実装し、全体の更新影響を抑える

## Directory Patterns

### Pythonパッケージ
**Location**: `/DownloadImagesOnPage/`
**Purpose**: 実装本体。CLI・ワークフロー・取得/解析/保存などをモジュール分割
**Example**:
- `main.py`: エントリポイント（ログ設定・終了コード）
- `cli.py`: 引数解析/バリデーション → `CLIConfig`
- `orchestrator.py`: 全体フローの制御（Playwright分岐もここ）
- `fetcher.py` / `parser.py` / `downloader.py` / `filter.py` / `file_manager.py`: 下位の責務
- `models.py`: dataclass/enum など共有モデル
- `exceptions.py`: カスタム例外階層

### テスト
**Location**: `/tests/`
**Purpose**: `pytest` によるユニット/CLI検証/統合/E2E（Playwright含む）
**Example**: CLI入力検証、重複ファイル名のE2E、Playwright連携など

### Steering（プロジェクト記憶）
**Location**: `/.kiro/steering/`
**Purpose**: パターンと意思決定の記録（ファイル一覧や仕様の網羅はしない）

## Naming Conventions

- **Files**: `snake_case.py`（Python慣習）
- **Public CLI command**: `DownloadImagesOnPage`（`pyproject.toml` の `project.scripts`）
- **Dataclass/Enum**: `PascalCase`（例: `CLIConfig`, `DownloadResult`）
- **Functions**: `snake_case`（例: `extract_image_urls`, `download_image`）

## Import Organization

- 基本は **パッケージ内の相対インポート**（例: `from .models import CLIConfig`）
- 共有層（`models`, `exceptions`）はどの層からも参照してよい
- **依存方向**: `main/cli/orchestrator` → 各機能モジュール（下位）
  - 下位モジュールは `orchestrator`/`main` を参照しない（循環依存を避ける）

## Code Organization Principles

- **オーケストレーションは1箇所**: フロー制御（分岐/集計/ログ）は `orchestrator` に集約
- **副作用を限定**: ダウンロード・ファイル書き込みは専用モジュールに閉じ込める
- **例外はドメイン例外に変換**: 外部ライブラリ例外をアプリ例外に包んで扱いを単純化
- **成功/失敗のサマリーを返す**: 関数が統計情報を返し、呼び出し側が表示/終了コードを決める

---
_パターンを記録し、ディレクトリツリーの網羅は避ける。新規コードが同じパターンに従うなら更新不要_
