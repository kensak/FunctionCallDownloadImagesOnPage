"""Tests for file manager module."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from io import BytesIO
import tempfile
import shutil

from DownloadImagesOnPage.file_manager import ensure_directory, generate_unique_filename, save_image
from DownloadImagesOnPage.exceptions import FileWriteError


class TestEnsureDirectory:
    """Tests for ensure_directory function."""
    
    def test_ensure_directory_creates_new_directory(self, tmp_path):
        """Should create directory if it doesn't exist."""
        new_dir = tmp_path / "test_output"
        assert not new_dir.exists()
        
        ensure_directory(new_dir)
        
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_ensure_directory_with_existing_directory(self, tmp_path):
        """Should succeed when directory already exists."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        assert existing_dir.exists()
        
        # Should not raise exception
        ensure_directory(existing_dir)
        
        assert existing_dir.exists()
        assert existing_dir.is_dir()
    
    def test_ensure_directory_creates_nested_directories(self, tmp_path):
        """Should create nested directory structure."""
        nested_dir = tmp_path / "level1" / "level2" / "level3"
        assert not nested_dir.exists()
        
        ensure_directory(nested_dir)
        
        assert nested_dir.exists()
        assert nested_dir.is_dir()
        assert (tmp_path / "level1").exists()
        assert (tmp_path / "level1" / "level2").exists()
    
    def test_ensure_directory_with_relative_path(self, tmp_path):
        """Should handle relative paths."""
        # Change to tmp_path and use relative path
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            relative_dir = Path("relative_output")
            
            ensure_directory(relative_dir)
            
            assert relative_dir.exists()
            assert relative_dir.is_dir()
        finally:
            os.chdir(original_cwd)
    
    def test_ensure_directory_raises_on_permission_error(self, tmp_path):
        """Should raise FileWriteError on permission error."""
        test_dir = tmp_path / "no_permission"
        
        with patch.object(Path, 'mkdir') as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("Permission denied")
            
            with pytest.raises(FileWriteError) as exc_info:
                ensure_directory(test_dir)
            
            error = exc_info.value
            assert error.path == test_dir
            assert "permission" in str(error).lower()
    
    def test_ensure_directory_raises_on_oserror(self, tmp_path):
        """Should raise FileWriteError on OSError."""
        test_dir = tmp_path / "os_error"
        
        with patch.object(Path, 'mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError("Disk full")
            
            with pytest.raises(FileWriteError) as exc_info:
                ensure_directory(test_dir)
            
            error = exc_info.value
            assert error.path == test_dir
    
    def test_ensure_directory_raises_on_file_exists_error(self, tmp_path):
        """Should raise FileWriteError when path exists as file."""
        # Create a file with the target name
        file_path = tmp_path / "file_not_dir"
        file_path.write_text("test")
        
        with pytest.raises(FileWriteError) as exc_info:
            ensure_directory(file_path)
        
        error = exc_info.value
        assert error.path == file_path
        assert "exists as a file" in str(error).lower() or "not a directory" in str(error).lower()
    
    def test_ensure_directory_handles_empty_directory_name(self, tmp_path):
        """Should handle current directory gracefully."""
        current_dir = Path(".")
        
        # Should not raise exception
        ensure_directory(current_dir)
        
        assert current_dir.exists()


class TestEnsureDirectoryEdgeCases:
    """Tests for edge cases in ensure_directory."""
    
    def test_ensure_directory_with_unicode_path(self, tmp_path):
        """Should handle Unicode characters in path."""
        unicode_dir = tmp_path / "日本語" / "テスト"
        
        ensure_directory(unicode_dir)
        
        assert unicode_dir.exists()
        assert unicode_dir.is_dir()
    
    def test_ensure_directory_with_spaces_in_path(self, tmp_path):
        """Should handle spaces in directory names."""
        spaced_dir = tmp_path / "my directory" / "with spaces"
        
        ensure_directory(spaced_dir)
        
        assert spaced_dir.exists()
        assert spaced_dir.is_dir()
    
    def test_ensure_directory_idempotent(self, tmp_path):
        """Should be idempotent - calling multiple times should work."""
        test_dir = tmp_path / "idempotent_test"
        
        ensure_directory(test_dir)
        ensure_directory(test_dir)
        ensure_directory(test_dir)
        
        assert test_dir.exists()
        assert test_dir.is_dir()
    
    def test_ensure_directory_with_very_long_path(self, tmp_path):
        """Should handle reasonably long paths."""
        # Create a moderately long path (not extreme to avoid OS limits)
        long_path = tmp_path
        for i in range(5):
            long_path = long_path / f"level_{i}_directory"
        
        ensure_directory(long_path)
        
        assert long_path.exists()
        assert long_path.is_dir()


class TestEnsureDirectoryIntegration:
    """Integration tests for ensure_directory."""
    
    def test_ensure_directory_full_workflow(self, tmp_path):
        """Should handle complete directory creation workflow."""
        # Create nested structure
        base_dir = tmp_path / "project"
        images_dir = base_dir / "images"
        thumbs_dir = base_dir / "thumbnails"
        
        ensure_directory(images_dir)
        ensure_directory(thumbs_dir)
        
        assert base_dir.exists()
        assert images_dir.exists()
        assert thumbs_dir.exists()
        assert all(d.is_dir() for d in [base_dir, images_dir, thumbs_dir])
    
    def test_ensure_directory_with_absolute_path(self, tmp_path):
        """Should handle absolute paths correctly."""
        absolute_dir = tmp_path / "absolute_test"
        absolute_path = absolute_dir.resolve()
        
        ensure_directory(absolute_path)
        
        assert absolute_path.exists()
        assert absolute_path.is_dir()


class TestGenerateUniqueFilename:
    """Tests for generate_unique_filename function."""
    
    def test_generate_unique_filename_no_conflict(self, tmp_path):
        """Should return original filename when no conflict exists."""
        filename = "image.jpg"
        
        result = generate_unique_filename(tmp_path, filename)
        
        assert result == tmp_path / "image.jpg"
        assert result.name == "image.jpg"
    
    def test_generate_unique_filename_with_conflict(self, tmp_path):
        """Should add _1 suffix when file already exists."""
        # Create existing file
        existing_file = tmp_path / "image.jpg"
        existing_file.write_text("existing")
        
        result = generate_unique_filename(tmp_path, "image.jpg")
        
        assert result == tmp_path / "image_1.jpg"
        assert result.name == "image_1.jpg"
    
    def test_generate_unique_filename_multiple_conflicts(self, tmp_path):
        """Should find next available number when multiple files exist."""
        # Create multiple existing files
        (tmp_path / "photo.png").write_text("1")
        (tmp_path / "photo_1.png").write_text("2")
        (tmp_path / "photo_2.png").write_text("3")
        
        result = generate_unique_filename(tmp_path, "photo.png")
        
        assert result == tmp_path / "photo_3.png"
    
    def test_generate_unique_filename_preserves_extension(self, tmp_path):
        """Should preserve file extension when adding suffix."""
        (tmp_path / "document.pdf").write_text("existing")
        
        result = generate_unique_filename(tmp_path, "document.pdf")
        
        assert result.suffix == ".pdf"
        assert result.name == "document_1.pdf"
    
    def test_generate_unique_filename_with_multiple_dots(self, tmp_path):
        """Should handle filenames with multiple dots correctly."""
        (tmp_path / "archive.tar.gz").write_text("existing")
        
        result = generate_unique_filename(tmp_path, "archive.tar.gz")
        
        # Should preserve the full extension
        assert result.name == "archive.tar_1.gz"
    
    def test_generate_unique_filename_no_extension(self, tmp_path):
        """Should handle files without extension."""
        (tmp_path / "README").write_text("existing")
        
        result = generate_unique_filename(tmp_path, "README")
        
        assert result.name == "README_1"
    
    def test_generate_unique_filename_gap_in_sequence(self, tmp_path):
        """Should find first available number even with gaps."""
        # Create files with gap (no _2)
        (tmp_path / "test.txt").write_text("0")
        (tmp_path / "test_1.txt").write_text("1")
        (tmp_path / "test_3.txt").write_text("3")
        
        result = generate_unique_filename(tmp_path, "test.txt")
        
        # Should use _2 (the first gap)
        assert result.name == "test_2.txt"
    
    def test_generate_unique_filename_returns_path_object(self, tmp_path):
        """Should return Path object."""
        result = generate_unique_filename(tmp_path, "file.jpg")
        
        assert isinstance(result, Path)
    
    def test_generate_unique_filename_with_spaces(self, tmp_path):
        """Should handle filenames with spaces."""
        (tmp_path / "my image.jpg").write_text("existing")
        
        result = generate_unique_filename(tmp_path, "my image.jpg")
        
        assert result.name == "my image_1.jpg"
    
    def test_generate_unique_filename_with_unicode(self, tmp_path):
        """Should handle Unicode characters in filename."""
        (tmp_path / "画像.jpg").write_text("existing")
        
        result = generate_unique_filename(tmp_path, "画像.jpg")
        
        assert result.name == "画像_1.jpg"


class TestGenerateUniqueFilenameEdgeCases:
    """Tests for edge cases in generate_unique_filename."""
    
    def test_generate_unique_filename_large_sequence_number(self, tmp_path):
        """Should handle large sequence numbers."""
        # Create many files
        for i in range(100):
            if i == 0:
                (tmp_path / "file.txt").write_text(str(i))
            else:
                (tmp_path / f"file_{i}.txt").write_text(str(i))
        
        result = generate_unique_filename(tmp_path, "file.txt")
        
        assert result.name == "file_100.txt"
    
    def test_generate_unique_filename_hidden_file(self, tmp_path):
        """Should handle hidden files (starting with dot)."""
        (tmp_path / ".hidden").write_text("existing")
        
        result = generate_unique_filename(tmp_path, ".hidden")
        
        assert result.name == ".hidden_1"
    
    def test_generate_unique_filename_only_extension(self, tmp_path):
        """Should handle files that are only extension."""
        (tmp_path / ".gitignore").write_text("existing")
        
        result = generate_unique_filename(tmp_path, ".gitignore")
        
        assert result.name == ".gitignore_1"
    
    def test_generate_unique_filename_empty_directory(self, tmp_path):
        """Should work with empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        result = generate_unique_filename(empty_dir, "first.jpg")
        
        assert result == empty_dir / "first.jpg"
    
    def test_generate_unique_filename_different_extensions_no_conflict(self, tmp_path):
        """Should not consider different extensions as conflicts."""
        (tmp_path / "file.jpg").write_text("jpg")
        (tmp_path / "file.png").write_text("png")
        
        # Asking for .txt should not conflict
        result = generate_unique_filename(tmp_path, "file.txt")
        
        assert result.name == "file.txt"


class TestGenerateUniqueFilenameIntegration:
    """Integration tests for generate_unique_filename."""
    
    def test_generate_unique_filename_workflow(self, tmp_path):
        """Should handle typical download workflow."""
        # Simulate downloading same image multiple times
        filenames = []
        for i in range(5):
            unique_path = generate_unique_filename(tmp_path, "download.jpg")
            filenames.append(unique_path.name)
            # Simulate saving the file
            unique_path.write_text(f"content_{i}")
        
        expected = ["download.jpg", "download_1.jpg", "download_2.jpg", 
                   "download_3.jpg", "download_4.jpg"]
        assert filenames == expected
    
    def test_generate_unique_filename_with_ensure_directory(self, tmp_path):
        """Should work together with ensure_directory."""
        output_dir = tmp_path / "downloads" / "images"
        ensure_directory(output_dir)
        
        result = generate_unique_filename(output_dir, "photo.png")
        
        assert result == output_dir / "photo.png"
        assert result.parent == output_dir


class TestSaveImage:
    """Tests for save_image function."""
    
    def test_save_image_writes_file(self, tmp_path):
        """Should write image data to file."""
        image_data = BytesIO(b"fake image content")
        file_path = tmp_path / "test.jpg"
        
        save_image(image_data, file_path)
        
        assert file_path.exists()
        assert file_path.read_bytes() == b"fake image content"
    
    def test_save_image_creates_new_file(self, tmp_path):
        """Should create new file if it doesn't exist."""
        image_data = BytesIO(b"new image")
        file_path = tmp_path / "new_image.png"
        
        save_image(image_data, file_path)
        
        assert file_path.exists()
        assert file_path.is_file()
    
    def test_save_image_overwrites_existing_file(self, tmp_path):
        """Should overwrite existing file."""
        file_path = tmp_path / "existing.jpg"
        file_path.write_bytes(b"old content")
        
        image_data = BytesIO(b"new content")
        save_image(image_data, file_path)
        
        assert file_path.read_bytes() == b"new content"
    
    def test_save_image_preserves_bytesio_position(self, tmp_path):
        """Should not modify BytesIO stream position permanently."""
        image_data = BytesIO(b"test data")
        image_data.read(4)  # Move position to 4
        file_path = tmp_path / "test.jpg"
        
        save_image(image_data, file_path)
        
        # Stream should be reset or not affected
        assert file_path.read_bytes() == b"test data"
    
    def test_save_image_handles_large_data(self, tmp_path):
        """Should handle large image data."""
        large_data = b"x" * 1000000  # 1MB
        image_data = BytesIO(large_data)
        file_path = tmp_path / "large.jpg"
        
        save_image(image_data, file_path)
        
        assert file_path.exists()
        assert len(file_path.read_bytes()) == 1000000
    
    def test_save_image_handles_empty_data(self, tmp_path):
        """Should handle empty image data."""
        image_data = BytesIO(b"")
        file_path = tmp_path / "empty.jpg"
        
        save_image(image_data, file_path)
        
        assert file_path.exists()
        assert file_path.read_bytes() == b""


class TestSaveImageErrors:
    """Tests for error handling in save_image."""
    
    def test_save_image_raises_on_permission_error(self, tmp_path):
        """Should raise FileWriteError on permission error."""
        image_data = BytesIO(b"test")
        file_path = tmp_path / "test.jpg"
        
        with patch.object(Path, 'write_bytes') as mock_write:
            mock_write.side_effect = PermissionError("Permission denied")
            
            with pytest.raises(FileWriteError) as exc_info:
                save_image(image_data, file_path)
            
            error = exc_info.value
            assert error.path == file_path
            assert "permission" in str(error).lower()
    
    def test_save_image_raises_on_oserror(self, tmp_path):
        """Should raise FileWriteError on OSError."""
        image_data = BytesIO(b"test")
        file_path = tmp_path / "test.jpg"
        
        with patch.object(Path, 'write_bytes') as mock_write:
            mock_write.side_effect = OSError("Disk full")
            
            with pytest.raises(FileWriteError) as exc_info:
                save_image(image_data, file_path)
            
            error = exc_info.value
            assert error.path == file_path
    
    def test_save_image_raises_on_ioerror(self, tmp_path):
        """Should raise FileWriteError on IOError."""
        image_data = BytesIO(b"test")
        file_path = tmp_path / "test.jpg"
        
        with patch.object(Path, 'write_bytes') as mock_write:
            mock_write.side_effect = IOError("I/O error")
            
            with pytest.raises(FileWriteError) as exc_info:
                save_image(image_data, file_path)
            
            error = exc_info.value
            assert error.path == file_path
            assert "i/o" in str(error).lower() or "error" in str(error).lower()
    
    def test_save_image_raises_on_readonly_directory(self, tmp_path):
        """Should raise FileWriteError when directory is read-only."""
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        file_path = readonly_dir / "test.jpg"
        image_data = BytesIO(b"test")
        
        with patch.object(Path, 'write_bytes') as mock_write:
            mock_write.side_effect = PermissionError("Read-only file system")
            
            with pytest.raises(FileWriteError) as exc_info:
                save_image(image_data, file_path)
            
            assert exc_info.value.path == file_path


class TestSaveImageEdgeCases:
    """Tests for edge cases in save_image."""
    
    def test_save_image_with_unicode_filename(self, tmp_path):
        """Should handle Unicode characters in filename."""
        image_data = BytesIO(b"test content")
        file_path = tmp_path / "画像.jpg"
        
        save_image(image_data, file_path)
        
        assert file_path.exists()
        assert file_path.read_bytes() == b"test content"
    
    def test_save_image_with_spaces_in_filename(self, tmp_path):
        """Should handle spaces in filename."""
        image_data = BytesIO(b"test content")
        file_path = tmp_path / "my image.jpg"
        
        save_image(image_data, file_path)
        
        assert file_path.exists()
        assert file_path.name == "my image.jpg"
    
    def test_save_image_with_nested_directory(self, tmp_path):
        """Should work with nested directory path."""
        nested_dir = tmp_path / "level1" / "level2"
        nested_dir.mkdir(parents=True)
        image_data = BytesIO(b"nested")
        file_path = nested_dir / "image.jpg"
        
        save_image(image_data, file_path)
        
        assert file_path.exists()
        assert file_path.read_bytes() == b"nested"
    
    def test_save_image_with_absolute_path(self, tmp_path):
        """Should handle absolute paths."""
        file_path = (tmp_path / "absolute.jpg").resolve()
        image_data = BytesIO(b"absolute")
        
        save_image(image_data, file_path)
        
        assert file_path.exists()
        assert file_path.read_bytes() == b"absolute"
    
    def test_save_image_binary_content(self, tmp_path):
        """Should handle actual binary image content."""
        # Simulate real image bytes (PNG header)
        png_header = b'\x89PNG\r\n\x1a\n'
        image_data = BytesIO(png_header + b"fake png data")
        file_path = tmp_path / "real.png"
        
        save_image(image_data, file_path)
        
        content = file_path.read_bytes()
        assert content.startswith(png_header)


class TestSaveImageIntegration:
    """Integration tests for save_image."""
    
    def test_save_image_with_ensure_directory(self, tmp_path):
        """Should work together with ensure_directory."""
        output_dir = tmp_path / "output"
        ensure_directory(output_dir)
        
        image_data = BytesIO(b"integrated")
        file_path = output_dir / "image.jpg"
        
        save_image(image_data, file_path)
        
        assert file_path.exists()
        assert file_path.read_bytes() == b"integrated"
    
    def test_save_image_with_generate_unique_filename(self, tmp_path):
        """Should work together with generate_unique_filename."""
        # Create existing file
        (tmp_path / "photo.jpg").write_bytes(b"existing")
        
        # Generate unique name and save
        unique_path = generate_unique_filename(tmp_path, "photo.jpg")
        image_data = BytesIO(b"new photo")
        save_image(image_data, unique_path)
        
        assert unique_path.name == "photo_1.jpg"
        assert unique_path.read_bytes() == b"new photo"
        # Original should be unchanged
        assert (tmp_path / "photo.jpg").read_bytes() == b"existing"
    
    def test_save_image_complete_workflow(self, tmp_path):
        """Should handle complete file management workflow."""
        # Setup directory
        output_dir = tmp_path / "downloads"
        ensure_directory(output_dir)
        
        # Save multiple images with same name
        for i in range(3):
            unique_path = generate_unique_filename(output_dir, "download.jpg")
            image_data = BytesIO(f"content_{i}".encode())
            save_image(image_data, unique_path)
        
        # Verify all files exist
        assert (output_dir / "download.jpg").exists()
        assert (output_dir / "download_1.jpg").exists()
        assert (output_dir / "download_2.jpg").exists()
        
        # Verify content
        assert (output_dir / "download.jpg").read_bytes() == b"content_0"
        assert (output_dir / "download_1.jpg").read_bytes() == b"content_1"
        assert (output_dir / "download_2.jpg").read_bytes() == b"content_2"


