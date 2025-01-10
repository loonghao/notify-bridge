"""WeChat Work (WeCom) notifier implementation."""

# Import built-in modules
import base64
import hashlib
import mimetypes
import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Import third-party modules
from PIL import Image
from pydantic import Field

# Import local modules
from notify_bridge.exceptions import NotificationError
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema
from notify_bridge.utils.requests import RequestsHelper


class WeComSchema(NotificationSchema):
    """Schema for WeCom notifications."""

    webhook_url: str = Field(..., description="The webhook URL to send notifications to")
    title: str = Field(..., description="The title of the notification")
    body: str = Field(..., description="The body of the notification")
    msg_type: str = Field("text", description="The type of message to send (text, markdown, news, image, file)")
    mentioned_list: Optional[List[str]] = Field(None, description="List of user IDs to mention (@)")
    mentioned_mobile_list: Optional[List[str]] = Field(None, description="List of mobile numbers to mention (@)")
    # For news type messages
    articles: Optional[List[dict]] = Field(None, description="List of articles for news type messages")
    # For file/image type messages
    file_path: Optional[str] = Field(None, description="Local file path to upload")
    file_url: Optional[str] = Field(None, description="URL of the file to upload")


class WeComNotifier(BaseNotifier):
    """Notifier for WeCom (WeChat Work)."""

    name = "wecom"
    schema = WeComSchema
    site_url = "https://work.weixin.qq.com/"

    # Supported file types
    SUPPORTED_IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".gif"}
    SUPPORTED_FILE_TYPES = {".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".rar"}

    # File size limits
    MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

    def __init__(self, webhook_url: Optional[str] = None, **kwargs):
        """Initialize the notifier.

        Args:
            webhook_url: The webhook URL to send notifications to.
            **kwargs: Additional configuration for the notifier.
        """
        super().__init__(**kwargs)
        self._webhook_url = webhook_url
        self._requests = RequestsHelper()
        self._key = self._extract_key_from_webhook(webhook_url) if webhook_url else None

    def _extract_key_from_webhook(self, webhook_url: str) -> str:
        """Extract key from webhook URL.

        Args:
            webhook_url: The webhook URL.

        Returns:
            The key from the webhook URL.
        """
        parsed = urlparse(webhook_url)
        query_params = dict(param.split("=") for param in parsed.query.split("&"))
        return query_params.get("key", "")

    def _is_local_file(self, path: str) -> bool:
        """Check if the path is a local file path.

        Args:
            path: The path to check.

        Returns:
            bool: True if the path is a local file path and exists.
        """
        # If it's a URL, return False
        if path.startswith(("http://", "https://", "ftp://")):
            return False

        # Try to convert the path to an absolute path
        try:
            abs_path = os.path.abspath(path)
            return os.path.isfile(abs_path)
        except Exception:
            return False

    def _validate_file_type(self, file_path: str, file_type: str) -> None:
        """Validate if the file type is supported.

        Args:
            file_path: Path to the file to validate.
            file_type: Type of the file ('image' or 'file').

        Raises:
            NotificationError: If the file type is not supported.
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            raise NotificationError(f"Unable to determine file type for {file_path}")

        if file_type == "image":
            if not mime_type.startswith("image/"):
                raise NotificationError(f"File {file_path} is not an image")
            # WeCom only supports JPG/PNG formats
            if mime_type not in {"image/jpeg", "image/png"}:
                raise NotificationError(f"Image type {mime_type} is not supported")
        elif file_type == "file":
            # WeCom supported file types
            allowed_types = {
                "application/msword",  # doc
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
                "application/vnd.ms-excel",  # xls
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx
                "application/vnd.ms-powerpoint",  # ppt
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # pptx
                "application/pdf",  # pdf
                "text/plain",  # txt
            }
            if mime_type not in allowed_types:
                raise NotificationError(f"File type {mime_type} is not supported")

    def _compress_image(self, image_path: str, max_size: int = MAX_IMAGE_SIZE) -> Tuple[str, str]:
        """Compress image if it exceeds the size limit.

        Args:
            image_path: Path to the image file.
            max_size: Maximum allowed size in bytes.

        Returns:
            Tuple[str, str]: Tuple of (compressed file path, file extension).
        """
        try:
            # Get original file size and extension
            file_size = os.path.getsize(image_path)
            _, ext = os.path.splitext(image_path.lower())

            # If file size is already within the limit and is a JPG/PNG format, return the original file
            if file_size <= max_size and ext in {".jpg", ".jpeg", ".png"}:
                return image_path, ext

            # Open the image
            with Image.open(image_path) as img:
                # If it's an animated image, convert it to a static image
                if getattr(img, "is_animated", False):
                    img.seek(0)  # Use the first frame

                # Limit the image dimensions
                max_dimension = 2048  # Maximum resolution
                if max(img.size) > max_dimension:
                    ratio = max_dimension / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Convert to RGB (if it's RGBA or P)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                    temp_path = temp_file.name

                # Initial quality
                quality = 95
                while quality > 5:
                    # Save the compressed image
                    img.save(temp_path, "JPEG", quality=quality, optimize=True)

                    # Check the file size
                    if os.path.getsize(temp_path) <= max_size:
                        return temp_path, ".jpg"

                    # Decrease quality and try again
                    quality -= 5

                # If quality is decreased to the minimum and still exceeds the size limit
                raise NotificationError("Unable to compress image to required size")

        except Exception as e:
            raise NotificationError(f"Failed to compress image: {str(e)}")

    async def _upload_media(self, file_path: str, file_type: str) -> str:
        """Upload media file to WeCom.

        Args:
            file_path: Path to the file to upload.
            file_type: Type of the file ('image' or 'file').

        Returns:
            The media_id of the uploaded file.

        Raises:
            NotificationError: If the file upload fails.
        """
        if not os.path.exists(file_path):
            raise NotificationError(f"File not found: {file_path}")

        # Validate file type
        self._validate_file_type(file_path, file_type)

        # Check and compress image (if necessary)
        temp_file = None
        try:
            if file_type == "image":
                file_path, _ = self._compress_image(file_path)
                temp_file = file_path

            # Check file size
            file_size = os.path.getsize(file_path)
            if file_type == "image" and file_size > self.MAX_IMAGE_SIZE:
                raise NotificationError("Image file size must be less than 2MB")
            elif file_type == "file" and file_size > self.MAX_FILE_SIZE:
                raise NotificationError("File size must be less than 20MB")

            upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={self._key}&type={file_type}"

            try:
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = "application/octet-stream"

                # For images, force using image/jpeg or image/png
                if file_type == "image":
                    ext = os.path.splitext(file_path)[1].lower()
                    mime_type = "image/jpeg" if ext in {".jpg", ".jpeg"} else "image/png"

                with open(file_path, "rb") as f:
                    files = {"media": (os.path.basename(file_path), f, mime_type)}
                    response = await self._requests.apost(upload_url, files=files)
                    response_data = response.json()

                    if response_data.get("errcode", 0) != 0:
                        raise NotificationError(
                            f"Failed to upload file: {response_data.get('errmsg', 'Unknown error')}"
                        )

                    return response_data.get("media_id", "")
            except Exception as e:
                raise NotificationError(f"Failed to upload file: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_file and temp_file != file_path and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    async def _download_and_upload_media(self, file_url: str, file_type: str) -> str:
        """Download file from URL and upload to WeCom.

        Args:
            file_url: URL of the file to download and upload.
            file_type: Type of the file ('image' or 'file').

        Returns:
            The media_id of the uploaded file.

        Raises:
            NotificationError: If the file download or upload fails.
        """
        try:
            response = await self._requests.aget(file_url)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            ext = mimetypes.guess_extension(content_type) or ".tmp"

            # Validate file type
            if file_type == "image" and ext.lower() not in self.SUPPORTED_IMAGE_TYPES:
                raise NotificationError(f"URL points to unsupported image type: {content_type}")

            # Create a temporary file
            file_name = os.path.basename(urlparse(file_url).path)
            if not file_name or "." not in file_name:
                file_name = f"temp{ext}"

            temp_path = os.path.join(tempfile.gettempdir(), file_name)
            try:
                with open(temp_path, "wb") as f:
                    f.write(response.content)
                return await self._upload_media(temp_path, file_type)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except Exception as e:
            raise NotificationError(f"Failed to download and upload file: {str(e)}")

    async def _process_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process articles for news message.

        Args:
            articles: List of articles.

        Returns:
            List[Dict[str, Any]]: List of processed articles.
        """
        processed_articles = []
        for article in articles:
            processed_article = article.copy()
            print(f"Processing article: {processed_article}")
            if "picurl" in article and self._is_local_file(article["picurl"]):
                try:
                    # Validate and compress image
                    image_path, _ = self._compress_image(article["picurl"])

                    # For news messages, directly use the base64 encoded image
                    with open(image_path, "rb") as f:
                        content = f.read()
                        hashlib.md5(content).hexdigest()
                        base64.b64encode(content).decode("utf-8")

                    # Upload the image
                    upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={self._key}&type=file"
                    files = {"media": ("image.jpg", content, "image/jpeg")}
                    response = await self._requests.apost(upload_url, files=files)
                    response_data = response.json()

                    if response_data.get("errcode", 0) != 0:
                        raise NotificationError(
                            f"Failed to upload image: {response_data.get('errmsg', 'Unknown error')}"
                        )

                    media_id = response_data.get("media_id", "")
                    if not media_id:
                        raise NotificationError("Failed to get media_id")

                    # Replace the local path with the WeCom image URL
                    processed_article["picurl"] = f"https://wework.qpic.cn/wwpic/{media_id}/0"
                    print(f"Processed article: {processed_article}")
                except Exception as e:
                    # If the upload fails, log the error but continue processing
                    print(f"Warning: Failed to upload image {article['picurl']}: {str(e)}")
            processed_articles.append(processed_article)
        return processed_articles

    async def _prepare_message(self, notification: WeComSchema) -> Dict[str, Any]:
        """Prepare the message payload.

        Args:
            notification: The notification data.

        Returns:
            The message payload.

        Raises:
            NotificationError: If the message type is not supported.
        """
        if notification.msg_type == "text":
            content = f"{notification.title}\n{notification.body}"
            return {
                "msgtype": "text",
                "text": {
                    "content": content,
                    "mentioned_list": notification.mentioned_list or [],
                    "mentioned_mobile_list": notification.mentioned_mobile_list or [],
                },
            }
        elif notification.msg_type == "markdown":
            content = f"# {notification.title}\n{notification.body}"
            return {"msgtype": "markdown", "markdown": {"content": content}}
        elif notification.msg_type == "news":
            if not notification.articles:
                raise NotificationError("Articles are required for news type messages")

            # Process articles with local images
            processed_articles = await self._process_articles(notification.articles)

            return {"msgtype": "news", "news": {"articles": processed_articles}}
        elif notification.msg_type == "image":
            if not (notification.file_path or notification.file_url):
                raise NotificationError("Either file_path or file_url must be provided for image messages")

            image_path = notification.file_path
            if notification.file_url:
                # If it's a URL, download it first
                response = await self._requests.aget(notification.file_url)
                response.raise_for_status()

                # Create a temporary file
                _, ext = os.path.splitext(urlparse(notification.file_url).path)
                if not ext:
                    content_type = response.headers.get("content-type", "")
                    ext = mimetypes.guess_extension(content_type) or ".jpg"

                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                    temp_file.write(response.content)
                    image_path = temp_file.name

            try:
                # Validate and compress image
                image_path, _ = self._compress_image(image_path)

                # Read the image content and calculate the MD5
                with open(image_path, "rb") as f:
                    content = f.read()
                    md5sum = hashlib.md5(content).hexdigest()
                    base64_content = base64.b64encode(content).decode("utf-8")

                return {"msgtype": "image", "image": {"base64": base64_content, "md5": md5sum}}
            finally:
                # Clean up the temporary file
                if notification.file_url and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except:
                        pass
        elif notification.msg_type == "file":
            if not (notification.file_path or notification.file_url):
                raise NotificationError("Either file_path or file_url must be provided for file messages")

            media_id = None
            if notification.file_path:
                media_id = await self._upload_media(notification.file_path, notification.msg_type)
            elif notification.file_url:
                media_id = await self._download_and_upload_media(notification.file_url, notification.msg_type)

            if not media_id:
                raise NotificationError("Failed to get media_id")

            return {"msgtype": notification.msg_type, notification.msg_type: {"media_id": media_id}}
        else:
            raise NotificationError(f"Unsupported message type: {notification.msg_type}")

    async def send(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification.

        Args:
            notification: The notification data.

        Returns:
            NotificationResponse: The response from the notification attempt.

        Raises:
            NotificationError: If sending the notification fails.
        """
        try:
            data = notification.model_dump()
            webhook_url = data.get("webhook_url") or self._webhook_url
            if not webhook_url:
                raise NotificationError("No webhook URL provided")

            payload = await self._prepare_message(notification)
            response = await self._requests.apost(webhook_url, json=payload)
            response_data = response.json()

            if response_data.get("errcode", 0) != 0:
                raise NotificationError(f"WeCom API error: {response_data.get('errmsg', 'Unknown error')}")

            return NotificationResponse(True, self.name, data, response_data)
        except Exception as e:
            raise NotificationError(f"Failed to send WeCom notification: {str(e)}")

    async def asend(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification asynchronously.

        Args:
            notification: The notification data.

        Returns:
            NotificationResponse: The response from the notification attempt.

        Raises:
            NotificationError: If sending the notification fails.
        """
        return await self.send(notification)

    def close(self) -> None:
        """Close any resources held by the notifier."""
        # Import built-in modules
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._requests.aclose())
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    async def aclose(self) -> None:
        """Close any resources held by the notifier asynchronously."""
        await self._requests.aclose()
