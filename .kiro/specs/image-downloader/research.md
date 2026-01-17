# Research & Design Decisions Template

---
**Purpose**: Capture discovery findings, architectural investigations, and rationale that inform the technical design.

**Usage**:
- Log research activities and outcomes during the discovery phase.
- Document design decision trade-offs that are too detailed for `design.md`.
- Provide references and evidence for future audits or reuse.
---

## Summary
- **Feature**: `image-downloader`
- **Discovery Scope**: New Feature (greenfield Python CLI application)
- **Key Findings**:
  - requests + BeautifulSoup4は2025年現在も標準的なPython Webスクレイピングスタック
  - Pillow (PIL) を使用して画像ヘッダーから寸法情報を取得可能
  - argparseは組み込みライブラリで型ヒントと組み合わせて使用可能
  - venv環境でPython 3.11の隔離された実行環境を提供

## Research Log

### Python Web Scraping Stack (2025)
- **Context**: URLからHTMLを取得して画像URLを抽出するための最適なライブラリを調査
- **Sources Consulted**:
  - Real Python: Beautiful Soup Web Scraper (https://realpython.com/beautiful-soup-web-scraper-python/)
  - LearnDataSci: Ultimate Guide to Web Scraping (https://www.learndatasci.com/tutorials/ultimate-guide-web-scraping-w-python-requests-and-beautifulsoup/)
  - GeeksforGeeks: Implementing Web Scraping with BeautifulSoup
- **Findings**:
  - `requests` ライブラリ: HTTPリクエストの標準ライブラリ、タイムアウトとエラーハンドリングが充実
  - `beautifulsoup4` (bs4): HTML/XML解析の事実上の標準、`lxml`パーサーで高速化可能
  - `html.parser` (標準ライブラリ): 依存なしで動作するが、`lxml`より低速
  - 相対URL→絶対URL変換は`urllib.parse.urljoin()`を使用
- **Implications**:
  - requirements.txt: `requests>=2.31.0`, `beautifulsoup4>=4.12.0`
  - オプションで`lxml>=5.0.0`を追加してパース性能向上
  - エラーハンドリング: `requests.exceptions`モジュールの例外階層を活用

### 画像サイズ検出とフィルタリング
- **Context**: ダウンロード前に画像の寸法を取得してフィルタリングする方法を調査
- **Sources Consulted**:
  - Pillow公式ドキュメント
  - Python image download best practices
- **Findings**:
  - **Pillow (PIL Fork)**: `Image.open(BytesIO(response.content))`で画像を開き、`.size`属性で(width, height)を取得
  - **HEAD Request Strategy**: 画像全体をダウンロードせず、HEADリクエストでContent-Lengthを確認後、部分ダウンロード（Range header）で最小バイト数から寸法を推定
  - **Trade-off**: HEADリクエスト+部分DL は複雑、実装の簡潔さからフルダウンロード→サイズチェック→保存判定を推奨
- **Implications**:
  - requirements.txt: `Pillow>=10.0.0`
  - 実装アプローチ: 画像をメモリにダウンロード→Pillow でサイズ取得→フィルタ判定→保存
  - サイズ取得失敗時は警告ログを出力してスキップ

### Command-Line Interface Design
- **Context**: Python 3.11の型ヒントを活用したCLI設計
- **Sources Consulted**:
  - Python公式: argparse documentation (https://docs.python.org/3/library/argparse.html)
  - Real Python: Build CLIs with argparse (https://realpython.com/command-line-interfaces-python-argparse/)
  - Reddit discussions on argparse type hints
- **Findings**:
  - argparse は標準ライブラリ、型ヒント対応は`Namespace`オブジェクトに属性として追加
  - 型安全性向上: `dataclass`でCLI引数を定義し、argparseの結果を変換する方法が推奨される
  - `--help`は自動生成、`formatter_class=argparse.RawDescriptionHelpFormatter`で説明文の整形が可能
- **Implications**:
  - CLIConfig dataclass を定義: `url: str`, `output_dir: Path`, `min_width: Optional[int]`, `min_height: Optional[int]`, `verbose: bool`
  - argparse結果を dataclass にマッピングして型安全性を確保

### File Naming and Duplication Avoidance
- **Context**: 同名ファイルの上書き防止戦略
- **Sources Consulted**: Python pathlib best practices
- **Findings**:
  - Strategy 1: 連番サフィックス（`image.jpg` → `image_1.jpg`, `image_2.jpg`）
  - Strategy 2: タイムスタンプベース（`image_20260117_093045.jpg`）
  - Strategy 3: ハッシュベース（URLのMD5 → `image_a3f2b1c.jpg`）
- **Implications**:
  - 実装推奨: Strategy 1 (連番サフィックス) がユーザーにとって最も直感的
  - `pathlib.Path.exists()`でチェック、存在する場合は`_1`, `_2`...を追加

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| Script-Based (Simple) | 単一Pythonスクリプト、関数ベース | 実装が簡潔、小規模プロジェクトに最適 | 拡張性低、テストしづらい | 要件が単純なため採用しない |
| Modular CLI | 機能ごとにモジュール分割、`main.py`がエントリーポイント | 関心の分離、テスト容易、拡張性高 | 初期構造設計が必要 | **選択**: 保守性とテストを考慮 |
| Class-Based | Downloader, Parser, Filterクラス | オブジェクト指向、状態管理が明確 | 過剰設計のリスク | 中間的な選択、モジュラーCLIで十分 |

## Design Decisions

### Decision: モジュラーCLI アーキテクチャ
- **Context**: 単一スクリプトか、複数モジュールに分割するか
- **Alternatives Considered**:
  1. 単一スクリプト — main関数にすべてのロジックを記述
  2. モジュラーCLI — 機能ごとにモジュール分割（fetcher, parser, downloader, cli）
- **Selected Approach**: モジュラーCLI
- **Rationale**:
  - 要件が9つあり、各機能（URL取得、HTML解析、画像DL、サイズフィルタ、CLI引数）の責務が明確
  - 単体テストが容易（各モジュールを独立してテスト可能）
  - 将来の拡張（CSS背景画像対応など）が容易
- **Trade-offs**:
  - 利点: 保守性、テスト容易性、拡張性
  - 欠点: ファイル数増加（5-6ファイル）、初期構造設計が必要
- **Follow-up**: モジュール間の依存関係を最小化、型ヒントで契約を明確化

### Decision: 画像サイズ取得戦略 - Full Download + In-Memory Check
- **Context**: ダウンロード前にサイズをチェックするか、ダウンロード後にチェックするか
- **Alternatives Considered**:
  1. HEAD + Range Request — HEADでサイズ確認、Rangeで部分DLして寸法推定
  2. Full Download + In-Memory Check — 画像を全てメモリDL、Pillowで寸法取得、フィルタ後保存
- **Selected Approach**: Full Download + In-Memory Check
- **Rationale**:
  - シンプルな実装: requests.get() → BytesIO → Pillow → size check
  - HEADリクエストは全サイトで対応していない（403エラーのリスク）
  - 画像サイズは通常数百KB〜数MBで、メモリに収まる
- **Trade-offs**:
  - 利点: 実装の単純さ、互換性の高さ
  - 欠点: 小画像もフルDLするため帯域消費（ただし要件上許容範囲）
- **Follow-up**: 大容量画像（>10MB）対応が必要になった場合はContent-Lengthチェックを追加

### Decision: ファイル名重複回避 - Numeric Suffix Strategy
- **Context**: 同名ファイルが存在する場合の命名戦略
- **Alternatives Considered**:
  1. Numeric Suffix — `image_1.jpg`, `image_2.jpg`
  2. Timestamp — `image_20260117_093045.jpg`
  3. Hash (URL MD5) — `image_a3f2b1c.jpg`
- **Selected Approach**: Numeric Suffix
- **Rationale**:
  - ユーザーが元のファイル名を推測しやすい
  - 連番は直感的で、ファイル順序が保たれる
- **Trade-offs**:
  - 利点: 可読性、シンプル
  - 欠点: 同じURLから複数回DLした場合の識別が難しい
- **Follow-up**: ハッシュベースは将来の拡張オプションとして検討

## Risks & Mitigations
- **Risk 1: 大規模ページで大量の画像が検出される** — Mitigation: 進捗表示とスキップ機能、タイムアウト設定
- **Risk 2: 非標準的なHTMLでBeautifulSoupの解析が失敗** — Mitigation: lxmlパーサーの使用、エラーハンドリングでスキップ
- **Risk 3: 画像URLがJavaScriptで動的生成される** — Mitigation: 現在の要件外、静的HTMLのみ対応（将来はSelenium検討）
- **Risk 4: メモリ不足（大量/大容量画像）** — Mitigation: 1枚ずつ処理、メモリ内に複数保持しない設計

## References
- [Real Python: Beautiful Soup Web Scraper](https://realpython.com/beautiful-soup-web-scraper-python/) — BeautifulSoup使用方法とベストプラクティス
- [Python argparse Documentation](https://docs.python.org/3/library/argparse.html) — 標準ライブラリargparseの公式リファレンス
- [Pillow Documentation](https://pillow.readthedocs.io/) — 画像処理ライブラリPillowの公式ドキュメント
- [LearnDataSci: Web Scraping Guide](https://www.learndatasci.com/tutorials/ultimate-guide-web-scraping-w-python-requests-and-beautifulsoup/) — requests + BeautifulSoup実践ガイド
