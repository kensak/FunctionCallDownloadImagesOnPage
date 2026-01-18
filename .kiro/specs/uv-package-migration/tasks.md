# Implementation Plan

## Task Overview
uvパッケージ移行の実装タスク。pyproject.tomlの作成、依存関係の移行、CLIエントリーポイントの設定、ドキュメント更新を含みます。

## Tasks

- [x] 1. pyproject.tomlの作成と基本設定 (P)
- [x] 1.1 (P) プロジェクトメタデータを定義
  - パッケージ名を`download-images-on-page`として設定
  - バージョンを`0.1.0`に設定
  - 説明文、README参照、Python最小バージョン（>=3.11）を記載
  - 著者情報（Ken Sakakibara）とMITライセンスを設定
  - PyPIトローブ分類子を追加（Development Status, Intended Audience, License, Programming Language, Topic）
  - _Requirements: 1.1, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [x] 1.2 (P) ビルドシステムを設定
  - `[build-system]`セクションにhatchlingを指定
  - `requires = ["hatchling"]`と`build-backend = "hatchling.build"`を定義
  - _Requirements: 1.3_

- [x] 1.3 (P) CLIエントリーポイントを定義
  - `[project.scripts]`セクションを追加
  - `DownloadImagesOnPage = "DownloadImagesOnPage.main:main"`を設定
  - 既存の`main.py`の`main()`関数を再利用
  - _Requirements: 1.2, 3.2, 4.1_

- [x] 2. 依存関係の移行と分離 (P)
- [x] 2.1 (P) 本番依存関係を定義
  - `[project.dependencies]`に現在のrequirements.txtから本番依存関係を移行
  - requests>=2.31.0, beautifulsoup4>=4.12.0, lxml>=5.0.0, Pillow>=10.0.0を記載
  - バージョン制約は現状の`>=`形式を維持
  - _Requirements: 2.1, 2.3_

- [x] 2.2 (P) 開発依存関係を分離
  - `[dependency-groups]`セクションに`dev`グループを作成
  - pytest>=7.4.0, pytest-cov>=4.1.0, pytest-mock>=3.12.0を記載
  - 本番インストール時に開発依存関係が除外されることを確認
  - _Requirements: 2.2, 2.4_

- [x] 3. 環境とビルドの検証
- [x] 3.1 開発環境をセットアップ
  - `uv sync --group dev`を実行して.venv環境を作成
  - 本番依存関係と開発依存関係の両方がインストールされることを確認
  - uv.lockファイルが生成されることを確認
  - _Requirements: 2.4_

- [x] 3.2 後方互換性を検証
  - `python -m DownloadImagesOnPage --help`を実行して動作確認
  - 既存のCLI機能（URL指定、出力ディレクトリ、--min-width, --min-height, --verbose）が正常に動作することを確認
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 3.3 既存テストスイートを実行
  - `uv run pytest`で全テストを実行
  - 全てのテストがパスすることを確認
  - テストカバレッジが維持されていることを確認
  - _Requirements: 7.4_

- [x] 4. パッケージビルドとインストール検証
- [x] 4.1 パッケージをビルド
  - `uv build`を実行してdist/ディレクトリにwheel + sdistを生成
  - 生成されたファイル（.whl, .tar.gz）の存在を確認
  - METADATAとentry_points.txtの内容を検証
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 4.2 uvツールとしてインストール
  - `uv tool install --force .`でローカルインストール
  - `which DownloadImagesOnPage`でコマンドがPATHに追加されたことを確認
  - 専用の分離環境（~/.local/share/uv/tools/）に配置されることを確認
  - _Requirements: 3.1, 3.4_

- [x] 4.3 インストールしたCLIを実行
  - `DownloadImagesOnPage --help`でヘルプが表示されることを確認
  - 実際のURLを使用して画像ダウンロードを実行
  - 全てのCLIオプション（--min-width, --min-height, --verbose）が正常に動作することを確認
  - _Requirements: 3.2, 3.3_

- [x] 4.4 uvxでの一時実行を検証
  - `uvx DownloadImagesOnPage --help`を実行
  - 依存関係が自動解決されて一時環境で実行されることを確認
  - 実行後に一時環境がクリーンアップされることを確認
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 5. ドキュメントの更新
- [x] 5.1 README.mdをuv対応に更新
  - 必要要件セクションにPython 3.11+とuvのインストール方法を追加
  - uvのインストール方法へのリンクを含める（https://docs.astral.sh/uv/getting-started/installation/）
  - _Requirements: 5.5_

- [x] 5.2 インストール方法セクションを書き直し
  - `uv tool install download-images-on-page`によるグローバルインストール方法を記載
  - `uvx DownloadImagesOnPage <URL> <dir>`による一時実行方法を追加
  - 従来のvenv + pip方式をレガシーセクションに移動または削除
  - _Requirements: 5.1, 5.2, 5.4_

- [x] 5.3 開発環境セットアップ手順を更新
  - `uv sync --group dev`による開発環境セットアップ手順を記載
  - `uv run pytest`によるテスト実行方法を記載
  - 従来のvenv + pip + pytest方式を削除
  - _Requirements: 5.3_

- [x] 5.4 使用例を更新
  - uvxを使用した基本的な使用例を追加
  - uv tool installした後のコマンド実行例を追加
  - python -mによる実行例も保持（後方互換性）
  - _Requirements: 5.2_

- [x] 5.5 pyproject.tomlのメタデータをREADMEに反映
  - repository URLやissues URLが追加された場合、それらをREADMEに記載
  - _Requirements: 5.6_

- [x] 6. requirements.txtの非推奨化または削除
- [x] 6.1 requirements.txtを処理
  - requirements.txtに非推奨コメントを追加、または完全に削除
  - pyproject.tomlへの移行を示すメッセージを残す場合は、その旨を記載
  - _Requirements: 1.5_

- [x] 7. 最終統合テスト
- [x] 7.1 全インストール方法を検証
  - uv tool installによるグローバルインストール → 実行確認
  - uvxによる一時実行 → 実行確認
  - python -mによるモジュール実行 → 実行確認（後方互換性）
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 7.1, 7.2_

- [x] 7.2 開発ワークフロー全体を検証
  - プロジェクトクローン → uv sync --group dev → uv run pytest → 全パス確認
  - 開発依存関係なしのインストール（uv sync）→ 本番依存関係のみ確認
  - _Requirements: 2.4_

- [x] 7.3* E2Eテストを実行（オプション）
  - 実際のWebページから画像をダウンロードするE2Eテストを実行
  - 最小サイズフィルタリング（--min-width, --min-height）が正常に機能することを確認
  - 詳細モード（--verbose）でログ出力を確認
  - _Requirements: 3.3, 4.2_

## Implementation Notes

### 推奨実装順序
1. タスク1-2は並行実行可能（pyproject.toml作成）
2. タスク3で環境検証（後方互換性とテスト）
3. タスク4でビルドとインストール検証
4. タスク5でドキュメント更新
5. タスク6でrequirements.txt削除
6. タスク7で最終統合テスト

### 重要な検証ポイント
- 各段階で既存機能が破壊されていないことを確認
- 後方互換性（python -m実行）は必須
- 全てのCLIオプションが3つの実行方法（uv tool install, uvx, python -m）で動作することを確認
