"""Data models for image downloader.

This module defines the core data structures used throughout the application:
- CLIConfig: Command-line configuration
- ImageDimensions: Image width and height
- DownloadStatus: Status enum for download operations
- ImageDownloadRecord: Individual image download record
- DownloadResult: Summary of download operation results
"""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import NamedTuple, Optional


@dataclass(frozen=True)
class CLIConfig:
    """コマンドライン引数の型安全な表現.
    
    Attributes:
        url: ダウンロード対象のWebページURL
        output_dir: 画像を保存する出力ディレクトリ
        min_width: 最小画像幅（ピクセル）、Noneの場合はフィルタリングしない
        min_height: 最小画像高さ（ピクセル）、Noneの場合はフィルタリングしない
        verbose: 詳細な出力を有効にするフラグ
    """
    
    url: str
    output_dir: Path
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    verbose: bool = False


class ImageDimensions(NamedTuple):
    """画像の寸法.
    
    Attributes:
        width: 画像の幅（ピクセル）
        height: 画像の高さ（ピクセル）
    """
    
    width: int
    height: int


class DownloadStatus(Enum):
    """ダウンロードステータス.
    
    Attributes:
        SUCCESS: 画像のダウンロードと保存に成功
        FAILED: ダウンロードまたは保存に失敗
        FILTERED: サイズフィルタにより除外
    """
    
    SUCCESS = "success"
    FAILED = "failed"
    FILTERED = "filtered"


@dataclass
class ImageDownloadRecord:
    """個別画像のダウンロード記録.
    
    Attributes:
        url: 画像のURL
        status: ダウンロードステータス
        file_path: 保存されたファイルパス（成功時のみ）
        dimensions: 画像の寸法（取得できた場合のみ）
        error_message: エラーメッセージ（失敗/フィルタ時のみ）
    """
    
    url: str
    status: DownloadStatus
    file_path: Optional[Path] = None
    dimensions: Optional[ImageDimensions] = None
    error_message: Optional[str] = None


@dataclass
class DownloadResult:
    """ダウンロード結果のサマリー.
    
    Attributes:
        success_count: 成功した画像の数
        failed_count: 失敗した画像の数
        filtered_count: フィルタで除外された画像の数
        total_count: 処理対象の画像の総数
    """
    
    success_count: int
    failed_count: int
    filtered_count: int
    total_count: int
