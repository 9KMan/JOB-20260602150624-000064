"""Image processing utilities."""

import logging
import io
from typing import Any
from urllib.parse import urlparse

import httpx
from PIL import Image

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Service for image processing operations."""

    SUPPORTED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}
    MAX_DIMENSION = 4096
    THUMBNAIL_SIZE = (200, 200)
    MEDIUM_SIZE = (800, 600)
    LARGE_SIZE = (1920, 1080)

    def __init__(self) -> None:
        """Initialize image processor."""
        self._http_client: httpx.AsyncClient | None = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def process_image_from_url(self, image_url: str) -> dict[str, Any] | None:
        """Process image from URL.

        Args:
            image_url: URL of the image

        Returns:
            Processed image data or None if failed
        """
        try:
            response = await self.http_client.get(image_url)
            response.raise_for_status()

            image_data = response.content
            return await self.process_image_data(image_data)

        except Exception as e:
            logger.error(f"Failed to process image from URL {image_url}: {e}")
            return None

    async def process_image_data(self, image_data: bytes) -> dict[str, Any] | None:
        """Process image data.

        Args:
            image_data: Raw image bytes

        Returns:
            Processed image data including thumbnails
        """
        try:
            image = Image.open(io.BytesIO(image_data))

            if image.format not in self.SUPPORTED_FORMATS:
                logger.warning(f"Unsupported image format: {image.format}")
                return None

            original_width, original_height = image.size

            if original_width > self.MAX_DIMENSION or original_height > self.MAX_DIMENSION:
                image = self._resize_image(image, self.MAX_DIMENSION)
                image_data = self._image_to_bytes(image)

            thumbnail = self._create_thumbnail(image, self.THUMBNAIL_SIZE)
            medium = self._resize_image(image, max(self.MEDIUM_SIZE))
            large = self._resize_image(image, max(self.LARGE_SIZE))

            return {
                "original": image_data,
                "thumbnail": self._image_to_bytes(thumbnail),
                "medium": self._image_to_bytes(medium),
                "large": self._image_to_bytes(large),
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "size": len(image_data),
            }

        except Exception as e:
            logger.error(f"Failed to process image data: {e}")
            return None

    def _resize_image(self, image: Image.Image, max_dimension: int) -> Image.Image:
        """Resize image maintaining aspect ratio.

        Args:
            image: PIL Image
            max_dimension: Maximum width or height

        Returns:
            Resized image
        """
        width, height = image.size

        if width <= max_dimension and height <= max_dimension:
            return image

        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def _create_thumbnail(self, image: Image.Image, size: tuple[int, int]) -> Image.Image:
        """Create thumbnail from image.

        Args:
            image: PIL Image
            size: Target size tuple (width, height)

        Returns:
            Thumbnail image
        """
        thumb = image.copy()
        thumb.thumbnail(size, Image.Resampling.LANCZOS)
        return thumb

    def _image_to_bytes(self, image: Image.Image, format: str = "JPEG") -> bytes:
        """Convert PIL Image to bytes.

        Args:
            image: PIL Image
            format: Output format

        Returns:
            Image bytes
        """
        buffer = io.BytesIO()

        if image.mode == "RGBA" and format == "JPEG":
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3])
            rgb_image.save(buffer, format=format, quality=85)
        else:
            image.save(buffer, format=format, quality=85)

        buffer.seek(0)
        return buffer.getvalue()

    async def optimize_image(
        self,
        image_data: bytes,
        quality: int = 85,
    ) -> bytes:
        """Optimize image for web.

        Args:
            image_data: Raw image bytes
            quality: JPEG quality (1-100)

        Returns:
            Optimized image bytes
        """
        try:
            image = Image.open(io.BytesIO(image_data))

            if image.mode == "RGBA":
                rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3])
                image = rgb_image

            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=quality, optimize=True)
            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to optimize image: {e}")
            return image_data

    async def get_image_metadata(self, image_url: str) -> dict[str, Any] | None:
        """Get image metadata without downloading full image.

        Args:
            image_url: URL of the image

        Returns:
            Image metadata or None if failed
        """
        try:
            parsed = urlparse(image_url)
            headers = {}

            async with self.http_client.stream("GET", image_url, headers=headers) as response:
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                content_length = response.headers.get("content-length")

                image_data = b""
                async for chunk in response.stream(8192):
                    image_data += chunk
                    if len(image_data) > 8192 * 10:
                        break

                image = Image.open(io.BytesIO(image_data))
                width, height = image.size

                return {
                    "url": image_url,
                    "content_type": content_type,
                    "content_length": int(content_length) if content_length else None,
                    "width": width,
                    "height": height,
                    "format": image.format,
                    "mode": image.mode,
                }

        except Exception as e:
            logger.error(f"Failed to get image metadata: {e}")
            return None