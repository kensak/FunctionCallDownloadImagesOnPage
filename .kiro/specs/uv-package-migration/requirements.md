# Requirements Document

## Project Description (Input)
このプロジェクトをuvのパッケージにして、uvのtoolとしてインストールしたりuvxで使えるようにして。dependenciesは開発用のものは区別して。ドキュメントも書き直して。

## Introduction
Image Downloaderプロジェクトを従来のrequirements.txt管理からuvパッケージマネージャーに移行し、uvのツールエコシステムに統合する。これにより、`uv tool install`や`uvx`コマンドでの簡単なインストールと実行が可能になり、開発依存関係と本番依存関係を明確に分離し、ドキュメントをuv対応形式に更新する。

## Requirements

### Requirement 1: uvパッケージ構成への移行
**Objective:** 開発者として、プロジェクトをuvパッケージとして管理したい。これにより、モダンなPythonパッケージ管理のベストプラクティスに従い、依存関係の管理を簡素化できる。

#### Acceptance Criteria
1. When プロジェクトルートにpyproject.tomlが存在する場合、the Image Downloader shall uvパッケージの標準メタデータ（name, version, description, authors, license）を含む
2. When pyproject.tomlが存在する場合、the Image Downloader shall `[project.scripts]`セクションにCLIエントリーポイント`DownloadImagesOnPage`を定義する
3. When pyproject.tomlが存在する場合、the Image Downloader shall `[build-system]`セクションでhatchlingまたはsetuptoolsをビルドバックエンドとして指定する
4. The Image Downloader shall Python 3.11以上を必須バージョンとして`[project]`セクションに指定する
5. When requirements.txtが存在する場合、the Image Downloader shall 移行後にそれを削除または非推奨マーカーで置き換える

### Requirement 2: 依存関係の分離
**Objective:** 開発者として、本番依存関係と開発依存関係を明確に分離したい。これにより、デプロイサイズを最小化し、開発環境のセットアップを明確にできる。

#### Acceptance Criteria
1. When pyproject.tomlが定義されている場合、the Image Downloader shall `[project.dependencies]`に本番依存関係（requests, beautifulsoup4, lxml, Pillow）を記載する
2. When pyproject.tomlが定義されている場合、the Image Downloader shall `[project.optional-dependencies.dev]`または`[dependency-groups.dev]`に開発依存関係（pytest, pytest-cov, pytest-mock）を記載する
3. The Image Downloader shall 各依存関係に適切なバージョン制約（>=, <, ~=など）を指定する
4. When 依存関係が分離されている場合、the Image Downloader shall 開発依存関係なしで本番インストールが可能である

### Requirement 3: uvツールとしてのインストール対応
**Objective:** ユーザーとして、`uv tool install`コマンドでツールをグローバルにインストールしたい。これにより、プロジェクト固有の環境を気にせずにツールを使用できる。

#### Acceptance Criteria
1. When `uv tool install`コマンドが実行された場合、the Image Downloader shall 正常にインストールされる
2. When uvツールとしてインストールされた場合、the Image Downloader shall `DownloadImagesOnPage`コマンドがシステムパスで利用可能になる
3. When インストール後にコマンドが実行された場合、the Image Downloader shall 既存のCLI機能（URL指定、出力ディレクトリ、オプション引数）が正常に動作する
4. The Image Downloader shall uvツール環境で隔離されたPython環境を使用し、他のツールと依存関係が競合しない

### Requirement 4: uvxでの実行対応
**Objective:** ユーザーとして、`uvx`コマンドでツールを一時的に実行したい。これにより、インストールせずに即座にツールを試用できる。

#### Acceptance Criteria
1. When `uvx DownloadImagesOnPage <URL> <出力ディレクトリ>`コマンドが実行された場合、the Image Downloader shall 依存関係を自動解決して実行される
2. When uvxで実行された場合、the Image Downloader shall すべてのCLIオプション（--min-width, --min-height, --verbose）が正常に機能する
3. When uvxでの実行が完了した場合、the Image Downloader shall 一時環境をクリーンアップする
4. The Image Downloader shall パッケージ名がPyPI公開用に適切に命名されている（例: image-downloader-cli）

### Requirement 5: ドキュメントの更新
**Objective:** ユーザーおよび開発者として、uvベースのワークフローに対応した最新のドキュメントを参照したい。これにより、セットアップと使用方法を正確に理解できる。

#### Acceptance Criteria
1. When README.mdが更新された場合、the Image Downloader shall uvを使用したインストール方法（`uv tool install`）を記載する
2. When README.mdが更新された場合、the Image Downloader shall uvxを使用した実行方法を記載する
3. When README.mdが更新された場合、the Image Downloader shall 開発環境のセットアップ手順を`uv sync --dev`または`uv sync --group dev`を使用した方法に更新する
4. When README.mdが更新された場合、the Image Downloader shall 従来のvenv + pip方式の手順を削除またはレガシーセクションに移動する
5. When README.mdが更新された場合、the Image Downloader shall Python 3.11+の必須要件とuvのインストール方法へのリンクを含む
6. If pyproject.tomlに追加のメタデータ（repository URL, issues URLなど）がある場合、the Image Downloader shall それらの情報をREADME.mdに反映する

### Requirement 6: パッケージメタデータの完全性
**Objective:** パッケージメンテナーとして、PyPI公開や配布に必要なメタデータを完備したい。これにより、将来的な公開や社内配布が容易になる。

#### Acceptance Criteria
1. The Image Downloader shall pyproject.tomlに明確なパッケージ名（例: `download-images-on-page`）を定義する
2. The Image Downloader shall セマンティックバージョニングに従ったバージョン番号（例: 0.1.0）を指定する
3. The Image Downloader shall 簡潔で明確なdescriptionフィールドを含む
4. The Image Downloader shall authorsフィールドに適切な著者情報を記載する
5. The Image Downloader shall licenseフィールド（例: MIT）を指定する
6. The Image Downloader shall readme フィールドでREADME.mdを指定する
7. The Image Downloader shall classifiersで適切なPyPIトローブ分類子（Development Status, Intended Audience, Programming Language等）を指定する

### Requirement 7: 後方互換性の維持
**Objective:** 既存ユーザーとして、移行後も`python -m DownloadImagesOnPage`による実行が可能であってほしい。これにより、既存スクリプトやワークフローが破壊されない。

#### Acceptance Criteria
1. When `python -m DownloadImagesOnPage`コマンドが実行された場合、the Image Downloader shall 引き続き正常に動作する
2. When モジュールとして実行された場合、the Image Downloader shall すべてのCLI機能が従来通り利用可能である
3. The Image Downloader shall __main__.pyおよびエントリーポイントが適切に維持される
4. If 既存テストが`python -m`形式での実行を想定している場合、the Image Downloader shall それらのテストが引き続きパスする
