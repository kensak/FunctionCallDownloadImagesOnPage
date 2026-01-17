# Requirements Document

## Project Description (Input)
venv でpython 3.11 の環境を作成した上で、与えられたURLのページに含まれる画像をすべて指定されたフォルダーに重複しない名前をつけて保存するpythonプログラムを作って。

## Introduction
本プロジェクトは、Webページから画像を自動的にダウンロードするPythonプログラムを作成します。ユーザーは指定したURLのページに含まれるすべての画像を、指定フォルダに重複なく保存できます。Python 3.11のvenv環境で動作します。

## Requirements

### Requirement 1: 環境セットアップ
**Objective:** 開発者として、Python 3.11のvenv環境を使用して、適切な依存関係がインストールされた状態でプログラムを実行したい。そうすることで、環境の一貫性と再現性を保証できる。

#### Acceptance Criteria
1. The image-downloader shall require Python 3.11 or higher
2. The image-downloader shall provide venv environment setup instructions
3. The image-downloader shall specify all required dependencies in requirements.txt
4. When venv環境がアクティブ化される, the image-downloader shall be executable without system-wide package conflicts

### Requirement 2: URL入力とページ取得
**Objective:** ユーザーとして、任意のWebページのURLを指定して、そのページの内容を取得したい。そうすることで、画像を抽出する対象を指定できる。

#### Acceptance Criteria
1. When ユーザーがURLを提供する, the image-downloader shall accept the URL as input parameter
2. When URLが提供される, the image-downloader shall retrieve the HTML content from the specified URL
3. If URLが無効または到達不可能である, then the image-downloader shall display a clear error message
4. If HTTPエラー（404, 500など）が発生する, then the image-downloader shall report the specific error code and terminate gracefully
5. The image-downloader shall support HTTP and HTTPS protocols

### Requirement 3: 画像検出と抽出
**Objective:** ユーザーとして、取得したHTMLページに含まれるすべての画像URLを検出したい。そうすることで、すべての画像をダウンロード対象として特定できる。

#### Acceptance Criteria
1. When HTMLコンテンツが取得される, the image-downloader shall parse all `<img>` tags
2. When HTMLコンテンツが取得される, the image-downloader shall extract image URLs from `src` attributes
3. When 相対URLが検出される, the image-downloader shall convert them to absolute URLs using the base URL
4. The image-downloader shall support common image formats (JPEG, PNG, GIF, WebP, SVG, BMP)
5. When CSS背景画像（background-image）が存在する, the image-downloader should optionally detect them
6. The image-downloader shall exclude data URIs and invalid image references

### Requirement 4: 保存先フォルダ指定
**Objective:** ユーザーとして、ダウンロードした画像を保存する先のフォルダを指定したい。そうすることで、画像を任意の場所に整理して保存できる。

#### Acceptance Criteria
1. When ユーザーが保存先フォルダパスを提供する, the image-downloader shall accept the folder path as input parameter
2. If 指定されたフォルダが存在しない, then the image-downloader shall create the folder automatically
3. If フォルダ作成に失敗する（権限不足など）, then the image-downloader shall display error message and terminate
4. The image-downloader shall validate the folder path before downloading

### Requirement 5: 画像ダウンロードと保存
**Objective:** ユーザーとして、検出されたすべての画像を指定フォルダにダウンロードしたい。そうすることで、ページ上の画像をローカルに保存できる。

#### Acceptance Criteria
1. When 画像URLリストが取得される, the image-downloader shall download each image
2. When 画像をダウンロードする, the image-downloader shall preserve the original file format
3. If 画像のダウンロードに失敗する（404, タイムアウトなど）, then the image-downloader shall skip that image and continue with others
4. The image-downloader shall display download progress (current/total images)
5. When すべてのダウンロードが完了する, the image-downloader shall report total success and failure counts

### Requirement 6: ファイル名の重複回避
**Objective:** ユーザーとして、同じ名前の画像が存在する場合に上書きされないようにしたい。そうすることで、すべての画像が失われることなく保存される。

#### Acceptance Criteria
1. When 保存先フォルダに同名のファイルが既に存在する, the image-downloader shall generate a unique filename
2. The image-downloader shall append a numeric suffix (e.g., `image_1.jpg`, `image_2.jpg`) to avoid conflicts
3. The image-downloader shall preserve the original file extension when generating unique names
4. When 複数の画像が同じ元ファイル名を持つ, the image-downloader shall increment the suffix sequentially
5. The image-downloader shall handle hash-based or timestamp-based naming as an alternative strategy

### Requirement 7: エラーハンドリングとロギング
**Objective:** 開発者/ユーザーとして、実行中のエラーや警告を明確に把握したい。そうすることで、問題のトラブルシューティングが容易になる。

#### Acceptance Criteria
1. When エラーが発生する, the image-downloader shall display descriptive error messages
2. The image-downloader shall log successful downloads and failures
3. If ネットワーク接続が失敗する, then the image-downloader shall provide network-related error information
4. The image-downloader shall continue execution after non-critical errors (e.g., single image download failure)
5. When 致命的なエラーが発生する（URL取得失敗など）, the image-downloader shall terminate with appropriate exit code

### Requirement 8: コマンドラインインターフェース
**Objective:** ユーザーとして、コマンドラインから簡単にプログラムを実行したい。そうすることで、スクリプトやバッチ処理に統合できる。

#### Acceptance Criteria
1. When プログラムが実行される, the image-downloader shall accept URL and folder path as command-line arguments
2. The image-downloader shall provide `--help` option to display usage instructions
3. If 必須引数が不足している, then the image-downloader shall display usage help and exit
4. The image-downloader shall support optional flags (e.g., `--verbose` for detailed output, `--min-width`, `--min-height`)
5. The image-downloader shall validate command-line arguments before execution

### Requirement 9: 画像サイズフィルタリング
**Objective:** ユーザーとして、最小画像サイズを指定して小さな画像を除外したい。そうすることで、サムネイルやアイコンなどの不要な小画像をダウンロードせずに済む。

#### Acceptance Criteria
1. When ユーザーが最小幅を指定する（`--min-width`）, the image-downloader shall filter out images narrower than the specified width
2. When ユーザーが最小高さを指定する（`--min-height`）, the image-downloader shall filter out images shorter than the specified height
3. When 最小幅と最小高さの両方が指定される, the image-downloader shall filter out images that do not meet both criteria
4. When 画像の寸法情報を取得できない, the image-downloader shall download the image header to determine dimensions before filtering
5. If 画像の寸法情報を取得できない場合, then the image-downloader shall skip that image and log a warning
6. The image-downloader shall report the number of images filtered out due to size constraints
7. When サイズフィルターオプションが指定されていない, the image-downloader shall download all detected images regardless of size

