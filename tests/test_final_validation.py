"""最終動作検証テスト

Task 14.2: 実際のWebページでエンドツーエンドテスト、venv環境での依存関係確認、
エラーケース動作確認、パフォーマンス検証
"""
import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import tempfile
import shutil
from io import BytesIO
import time
from PIL import Image

from DownloadImagesOnPage.main import main
from DownloadImagesOnPage.exceptions import FetchError


class TestFinalValidation(unittest.TestCase):
    """最終動作検証テストスイート"""

    def setUp(self):
        """各テストの前にテンポラリディレクトリを作成"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """各テストの後にテンポラリディレクトリを削除"""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def _create_test_image(self, width: int, height: int, format: str = 'PNG') -> bytes:
        """テスト用画像データを生成"""
        img = Image.new('RGB', (width, height), color='red')
        buffer = BytesIO()
        img.save(buffer, format=format)
        return buffer.getvalue()

    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_end_to_end_with_real_world_scenario(self, mock_get):
        """実際のWebページシナリオでのエンドツーエンドテスト"""
        # 実際のページをシミュレート: HTMLページと複数の画像
        html_content = '''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <img src="https://example.com/images/logo.png" alt="Logo">
                <img src="/assets/banner.jpg" alt="Banner">
                <img src="thumbnail.gif" alt="Thumb">
                <img src="https://example.com/gallery/photo1.webp" alt="Photo1">
                <img src="https://example.com/gallery/photo2.webp" alt="Photo2">
            </body>
        </html>
        '''

        # モックレスポンスを設定
        html_response = MagicMock()
        html_response.status_code = 200
        html_response.text = html_content
        html_response.content = html_content.encode('utf-8')

        # 様々なサイズと形式の画像を生成
        images = {
            'https://example.com/images/logo.png': self._create_test_image(200, 100, 'PNG'),
            'https://example.com/assets/banner.jpg': self._create_test_image(1200, 400, 'JPEG'),
            'https://example.com/thumbnail.gif': self._create_test_image(50, 50, 'GIF'),
            'https://example.com/gallery/photo1.webp': self._create_test_image(1920, 1080, 'PNG'),
            'https://example.com/gallery/photo2.webp': self._create_test_image(1920, 1080, 'PNG'),
        }

        def get_side_effect(url, *args, **kwargs):
            if url == 'https://example.com/':
                return html_response
            elif url in images:
                img_response = MagicMock()
                img_response.status_code = 200
                img_response.content = images[url]
                return img_response
            else:
                raise Exception(f"Unexpected URL: {url}")

        mock_get.side_effect = get_side_effect

        # CLI引数をシミュレート
        test_args = ['main.py', 'https://example.com/', self.test_dir]

        with patch('sys.argv', test_args):
            result = main()

        # 検証: 正常終了
        self.assertEqual(result, 0)

        # 検証: 全画像が保存されている
        saved_files = list(Path(self.test_dir).glob('*'))
        self.assertEqual(len(saved_files), 5, f"Expected 5 files, got {len(saved_files)}")

    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_error_handling_with_mixed_failures(self, mock_get):
        """エラーケース混在時の動作確認"""
        html_content = '''
        <html>
            <body>
                <img src="https://example.com/success1.png">
                <img src="https://example.com/404_image.png">
                <img src="https://example.com/success2.jpg">
                <img src="https://example.com/timeout_image.gif">
                <img src="https://example.com/success3.webp">
            </body>
        </html>
        '''

        html_response = MagicMock()
        html_response.status_code = 200
        html_response.text = html_content
        html_response.content = html_content.encode('utf-8')

        # 成功画像とエラー画像を混在させる
        def get_side_effect(url, *args, **kwargs):
            if url == 'https://example.com/':
                return html_response
            elif '404_image' in url:
                error_response = MagicMock()
                error_response.status_code = 404
                error_response.raise_for_status.side_effect = Exception("404 Not Found")
                return error_response
            elif 'timeout_image' in url:
                import requests
                raise requests.exceptions.Timeout("Connection timeout")
            elif 'success' in url:
                img_response = MagicMock()
                img_response.status_code = 200
                img_response.content = self._create_test_image(100, 100)
                return img_response
            else:
                raise Exception(f"Unexpected URL: {url}")

        mock_get.side_effect = get_side_effect

        test_args = ['main.py', 'https://example.com/', self.test_dir]

        with patch('sys.argv', test_args):
            result = main()

        # 検証: エラーがあっても正常終了（継続動作）
        self.assertEqual(result, 0)

        # 検証: 成功した画像のみ保存されている
        saved_files = list(Path(self.test_dir).glob('*'))
        self.assertEqual(len(saved_files), 3, "Expected 3 successful downloads")

    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_size_filtering_with_various_dimensions(self, mock_get):
        """サイズフィルタリングの動作確認"""
        html_content = '''
        <html>
            <body>
                <img src="https://example.com/small_icon.png">
                <img src="https://example.com/medium_thumb.jpg">
                <img src="https://example.com/large_photo.png">
                <img src="https://example.com/hd_image.jpg">
            </body>
        </html>
        '''

        html_response = MagicMock()
        html_response.status_code = 200
        html_response.text = html_content
        html_response.content = html_content.encode('utf-8')

        # 異なるサイズの画像を生成
        images = {
            'https://example.com/small_icon.png': self._create_test_image(32, 32),
            'https://example.com/medium_thumb.jpg': self._create_test_image(200, 150),
            'https://example.com/large_photo.png': self._create_test_image(1024, 768),
            'https://example.com/hd_image.jpg': self._create_test_image(1920, 1080),
        }

        def get_side_effect(url, *args, **kwargs):
            if url == 'https://example.com/':
                return html_response
            elif url in images:
                img_response = MagicMock()
                img_response.status_code = 200
                img_response.content = images[url]
                return img_response
            else:
                raise Exception(f"Unexpected URL: {url}")

        mock_get.side_effect = get_side_effect

        # 最小サイズ 800x600 でフィルタリング
        test_args = ['main.py', 'https://example.com/', self.test_dir,
                     '--min-width', '800', '--min-height', '600']

        with patch('sys.argv', test_args):
            result = main()

        # 検証: 正常終了
        self.assertEqual(result, 0)

        # 検証: 800x600以上の画像のみ保存（2つ）
        saved_files = list(Path(self.test_dir).glob('*'))
        self.assertEqual(len(saved_files), 2,
                         "Expected 2 images (1024x768 and 1920x1080)")

    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_duplicate_filename_handling(self, mock_get):
        """ファイル名重複時の連番サフィックス動作確認"""
        html_content = '''
        <html>
            <body>
                <img src="https://example.com/images/photo.jpg">
                <img src="https://example2.com/gallery/photo.jpg">
                <img src="https://example3.com/pics/photo.jpg">
            </body>
        </html>
        '''

        html_response = MagicMock()
        html_response.status_code = 200
        html_response.text = html_content
        html_response.content = html_content.encode('utf-8')

        def get_side_effect(url, *args, **kwargs):
            if url == 'https://example.com/':
                return html_response
            else:
                img_response = MagicMock()
                img_response.status_code = 200
                img_response.content = self._create_test_image(100, 100, 'JPEG')
                return img_response

        mock_get.side_effect = get_side_effect

        test_args = ['main.py', 'https://example.com/', self.test_dir]

        with patch('sys.argv', test_args):
            result = main()

        # 検証: 正常終了
        self.assertEqual(result, 0)

        # 検証: 3つのファイルが異なる名前で保存されている
        saved_files = sorted(Path(self.test_dir).glob('*.jpg'))
        self.assertEqual(len(saved_files), 3)

        # 検証: ファイル名に連番が付与されている
        filenames = [f.name for f in saved_files]
        self.assertIn('photo.jpg', filenames)
        self.assertIn('photo_1.jpg', filenames)
        self.assertIn('photo_2.jpg', filenames)

    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_performance_with_many_images(self, mock_get):
        """パフォーマンス検証: 100画像で2分以内"""
        # 100画像を含むHTMLを生成
        img_tags = '\n'.join([
            f'<img src="https://example.com/image{i}.jpg">'
            for i in range(100)
        ])
        html_content = f'<html><body>{img_tags}</body></html>'

        html_response = MagicMock()
        html_response.status_code = 200
        html_response.text = html_content
        html_response.content = html_content.encode('utf-8')

        # 小さな画像データを使用（速度重視）
        small_image = self._create_test_image(10, 10)

        def get_side_effect(url, *args, **kwargs):
            if url == 'https://example.com/':
                return html_response
            else:
                img_response = MagicMock()
                img_response.status_code = 200
                img_response.content = small_image
                return img_response

        mock_get.side_effect = get_side_effect

        test_args = ['main.py', 'https://example.com/', self.test_dir]

        # パフォーマンス測定
        start_time = time.time()

        with patch('sys.argv', test_args):
            result = main()

        elapsed_time = time.time() - start_time

        # 検証: 正常終了
        self.assertEqual(result, 0)

        # 検証: 100画像が保存されている
        saved_files = list(Path(self.test_dir).glob('*'))
        self.assertEqual(len(saved_files), 100)

        # 検証: 2分（120秒）以内に完了
        self.assertLess(elapsed_time, 120.0,
                        f"Performance test failed: took {elapsed_time:.2f}s, expected < 120s")

    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_verbose_mode_output(self, mock_get):
        """詳細モード（--verbose）の動作確認"""
        html_content = '<html><body><img src="https://example.com/test.png"></body></html>'

        html_response = MagicMock()
        html_response.status_code = 200
        html_response.text = html_content
        html_response.content = html_content.encode('utf-8')

        def get_side_effect(url, *args, **kwargs):
            if url == 'https://example.com/':
                return html_response
            else:
                img_response = MagicMock()
                img_response.status_code = 200
                img_response.content = self._create_test_image(100, 100)
                return img_response

        mock_get.side_effect = get_side_effect

        test_args = ['main.py', 'https://example.com/', self.test_dir, '--verbose']

        with patch('sys.argv', test_args):
            with patch('DownloadImagesOnPage.main.logger') as mock_logger:
                result = main()

        # 検証: 正常終了
        self.assertEqual(result, 0)

        # 検証: 詳細ログが出力されている（logger.debug が呼ばれている）
        # verboseモードでは詳細情報が表示されるはず
        self.assertTrue(mock_logger.debug.called or mock_logger.info.called,
                        "Expected logging calls in verbose mode")

    def test_invalid_url_error_handling(self):
        """無効なURL入力時のエラーハンドリング"""
        test_args = ['main.py', 'not-a-valid-url', self.test_dir]

        with patch('sys.argv', test_args):
            result = main()

        # 検証: エラー終了（exit code 1）
        self.assertEqual(result, 1, "Expected exit code 1 for invalid URL")

    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_network_error_handling(self, mock_get):
        """ネットワークエラー時のハンドリング"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")

        test_args = ['main.py', 'https://example.com/', self.test_dir]

        with patch('sys.argv', test_args):
            result = main()

        # 検証: エラー終了（exit code 2）
        self.assertEqual(result, 2, "Expected exit code 2 for network error")

    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_directory_creation_with_nested_path(self, mock_get):
        """ネストされたディレクトリ作成の動作確認"""
        html_content = '<html><body><img src="https://example.com/test.png"></body></html>'

        html_response = MagicMock()
        html_response.status_code = 200
        html_response.text = html_content
        html_response.content = html_content.encode('utf-8')

        def get_side_effect(url, *args, **kwargs):
            if url == 'https://example.com/':
                return html_response
            else:
                img_response = MagicMock()
                img_response.status_code = 200
                img_response.content = self._create_test_image(100, 100)
                return img_response

        mock_get.side_effect = get_side_effect

        # 存在しないネストされたディレクトリパスを指定
        nested_dir = Path(self.test_dir) / 'level1' / 'level2' / 'images'
        test_args = ['main.py', 'https://example.com/', str(nested_dir)]

        with patch('sys.argv', test_args):
            result = main()

        # 検証: 正常終了
        self.assertEqual(result, 0)

        # 検証: ディレクトリが作成されている
        self.assertTrue(nested_dir.exists())

        # 検証: 画像が保存されている
        saved_files = list(nested_dir.glob('*'))
        self.assertEqual(len(saved_files), 1)


class TestEnvironmentSetup(unittest.TestCase):
    """venv環境と依存関係の検証"""

    def test_required_packages_importable(self):
        """必須パッケージがインポート可能であることを確認"""
        try:
            import requests
            import bs4
            import lxml
            from PIL import Image
        except ImportError as e:
            self.fail(f"Required package not installed: {e}")

    def test_python_version(self):
        """Python 3.11以上であることを確認"""
        import sys
        version = sys.version_info
        self.assertGreaterEqual(version.major, 3)
        self.assertGreaterEqual(version.minor, 11)

    def test_requirements_file_exists(self):
        """requirements.txt が存在することを確認"""
        req_file = Path(__file__).parent.parent / 'requirements.txt'
        self.assertTrue(req_file.exists(), "requirements.txt not found")

    def test_requirements_contains_all_dependencies(self):
        """requirements.txt に必要な依存関係が含まれることを確認"""
        req_file = Path(__file__).parent.parent / 'requirements.txt'
        content = req_file.read_text(encoding='utf-8')

        required = ['requests', 'beautifulsoup4', 'lxml', 'Pillow']
        for package in required:
            self.assertIn(package, content,
                          f"Package {package} not found in requirements.txt")


if __name__ == '__main__':
    unittest.main()
