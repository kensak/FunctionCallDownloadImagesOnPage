"""Tests for HTML parser module."""
import pytest

from DownloadImagesOnPage.parser import extract_image_urls


class TestExtractImageUrlsBasic:
    """Tests for basic image URL extraction."""
    
    def test_extract_single_image_url(self):
        """Should extract single image URL."""
        html = '<html><body><img src="image.jpg"/></body></html>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert "https://example.com/image.jpg" in result
    
    def test_extract_multiple_image_urls(self):
        """Should extract multiple image URLs."""
        html = '''
        <html><body>
            <img src="image1.jpg"/>
            <img src="image2.png"/>
            <img src="image3.gif"/>
        </body></html>
        '''
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 3
        assert "https://example.com/image1.jpg" in result
        assert "https://example.com/image2.png" in result
        assert "https://example.com/image3.gif" in result
    
    def test_extract_absolute_url(self):
        """Should keep absolute URLs as-is."""
        html = '<img src="https://cdn.example.com/photo.jpg"/>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert "https://cdn.example.com/photo.jpg" in result
    
    def test_extract_returns_empty_list_for_no_images(self):
        """Should return empty list when no images found."""
        html = '<html><body><p>No images here</p></body></html>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert result == []


class TestExtractImageUrlsFormats:
    """Tests for supported image format extraction."""
    
    def test_extract_jpg_images(self):
        """Should extract .jpg images."""
        html = '<img src="photo.jpg"/>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
    
    def test_extract_jpeg_images(self):
        """Should extract .jpeg images."""
        html = '<img src="photo.jpeg"/>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
    
    def test_extract_png_images(self):
        """Should extract .png images."""
        html = '<img src="logo.png"/>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
    
    def test_extract_gif_images(self):
        """Should extract .gif images."""
        html = '<img src="animation.gif"/>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
    
    def test_extract_webp_images(self):
        """Should extract .webp images."""
        html = '<img src="modern.webp"/>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
    
    def test_extract_svg_images(self):
        """Should extract .svg images."""
        html = '<img src="icon.svg"/>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
    
    def test_extract_bmp_images(self):
        """Should extract .bmp images."""
        html = '<img src="bitmap.bmp"/>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
    
    def test_exclude_unsupported_format(self):
        """Should exclude unsupported image formats."""
        html = '<img src="file.txt"/><img src="photo.jpg"/>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert "photo.jpg" in result[0]


class TestExtractImageUrlsRelativePaths:
    """Tests for relative URL resolution."""
    
    def test_extract_relative_url_from_root(self):
        """Should resolve relative URL from root."""
        html = '<img src="/images/photo.jpg"/>'
        base_url = "https://example.com/page"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert result[0] == "https://example.com/images/photo.jpg"
    
    def test_extract_relative_url_same_directory(self):
        """Should resolve relative URL in same directory."""
        html = '<img src="photo.jpg"/>'
        base_url = "https://example.com/blog/"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert result[0] == "https://example.com/blog/photo.jpg"
    
    def test_extract_relative_url_subdirectory(self):
        """Should resolve relative URL with subdirectory."""
        html = '<img src="images/photo.jpg"/>'
        base_url = "https://example.com/blog/"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert result[0] == "https://example.com/blog/images/photo.jpg"
    
    def test_extract_relative_url_parent_directory(self):
        """Should resolve relative URL with parent directory."""
        html = '<img src="../photo.jpg"/>'
        base_url = "https://example.com/blog/post/"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert result[0] == "https://example.com/blog/photo.jpg"


class TestExtractImageUrlsFiltering:
    """Tests for URL filtering and exclusion."""
    
    def test_exclude_data_uri(self):
        """Should exclude data URIs."""
        html = '''
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA"/>
        <img src="photo.jpg"/>
        '''
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert "photo.jpg" in result[0]
    
    def test_exclude_empty_src(self):
        """Should exclude images with empty src."""
        html = '''
        <img src=""/>
        <img src="photo.jpg"/>
        '''
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert "photo.jpg" in result[0]
    
    def test_exclude_javascript_protocol(self):
        """Should exclude javascript: protocol."""
        html = '''
        <img src="javascript:void(0)"/>
        <img src="photo.jpg"/>
        '''
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert "photo.jpg" in result[0]
    
    def test_exclude_mailto_protocol(self):
        """Should exclude mailto: protocol."""
        html = '''
        <img src="mailto:test@example.com"/>
        <img src="photo.jpg"/>
        '''
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert "photo.jpg" in result[0]
    
    def test_remove_duplicates(self):
        """Should remove duplicate URLs."""
        html = '''
        <img src="photo.jpg"/>
        <img src="photo.jpg"/>
        <img src="other.png"/>
        '''
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 2
        assert "https://example.com/photo.jpg" in result
        assert "https://example.com/other.png" in result


class TestExtractImageUrlsEdgeCases:
    """Tests for edge cases."""
    
    def test_extract_from_empty_html(self):
        """Should handle empty HTML."""
        html = ""
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert result == []
    
    def test_extract_with_malformed_html(self):
        """Should handle malformed HTML."""
        html = '<img src="photo.jpg"<img src="other.png"/>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        # BeautifulSoup should still extract what it can
        assert len(result) >= 1
    
    def test_extract_case_insensitive_extensions(self):
        """Should handle case-insensitive file extensions."""
        html = '''
        <img src="photo.JPG"/>
        <img src="logo.PNG"/>
        '''
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 2
    
    def test_extract_with_query_parameters(self):
        """Should preserve query parameters in URLs."""
        html = '<img src="photo.jpg?size=large&quality=high"/>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert "?size=large&quality=high" in result[0]
    
    def test_extract_with_fragment(self):
        """Should preserve URL fragments."""
        html = '<img src="photo.jpg#section"/>'
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert "#section" in result[0]
    
    def test_extract_img_without_src_attribute(self):
        """Should skip img tags without src attribute."""
        html = '''
        <img alt="photo"/>
        <img src="photo.jpg"/>
        '''
        base_url = "https://example.com"
        
        result = extract_image_urls(html, base_url)
        
        assert len(result) == 1
        assert "photo.jpg" in result[0]
