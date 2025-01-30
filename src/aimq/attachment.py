"""
Attachment handling module for AIMQ.

This module provides functionality for handling file attachments in tasks,
including file type detection and content handling.
"""

import io
from typing import Any, Iterable, Optional, Tuple, Union

import filetype  # type: ignore
import humanize
from PIL import Image
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, computed_field


class Attachment(BaseModel):
    """A file attachment that can be included with a task.

    Attributes:
        data: The bytes of the attachment.
        mimetype: The MIME type of the file.
        extension: The file extension.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: bytes = Field(..., description="The bytes of the attachment", exclude=True)

    _mimetype: str = PrivateAttr(default="application/octet-stream")
    _extension: Optional[str] = PrivateAttr(default=None)

    @computed_field  # type: ignore
    @property
    def mimetype(self) -> str:
        """Get the MIME type of the attachment.

        Returns:
            str: MIME type of the attachment.
        """
        return self._mimetype

    @computed_field  # type: ignore
    @property
    def extension(self) -> Optional[str]:
        """Get the file extension of the attachment.

        Returns:
            Optional[str]: File extension of the attachment.
        """
        return self._extension

    def model_post_init(self, __context: Any) -> None:
        """Initialize the attachment after creation.

        This method is called after the attachment is created to detect the file type.

        Args:
            __context: Pydantic initialization context.
        """
        kind = filetype.guess(self.data)
        if kind:
            self._mimetype = kind.mime
            self._extension = kind.extension
        else:
            self._mimetype = "application/octet-stream"
            self._extension = None

    @computed_field  # type: ignore
    def size(self) -> str:
        """Get the size of the attachment.

        Returns:
            str: Human-readable size of the attachment.
        """
        return humanize.naturalsize(len(self.data))  # type: ignore

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Union[str, bytes, None]:
        """Get an attribute of the attachment.

        Args:
            key: The attribute to get.
            default: The default value to return if the attribute is not found.

        Returns:
            Union[str, bytes, None]: The attribute value or the default value.
        """
        if hasattr(self, key):
            value = getattr(self, key, default)
            if isinstance(value, (str, bytes)) or value is None:
                return value
            return str(value)
        return default

    def __repr_args__(self) -> Iterable[Tuple[str, Any]]:
        """Get the representation arguments of the attachment.

        Returns:
            Iterable[Tuple[str, Any]]: Iterable of tuples containing attribute names and
                values.
        """
        exclude_fields = {"data", "_mimetype", "_extension"}
        attrs = self.model_dump(exclude=exclude_fields).items()
        return [(a, v) for a, v in attrs if v is not None]

    def to_file(self) -> Image.Image:
        """Get the attachment as a file.

        Returns:
            Image.Image: The attachment as a PIL Image object.

        Raises:
            ValueError: If the data or mimetype is not provided, or if not an image.
        """
        if not self.data or not self.mimetype:
            raise ValueError("Data or mimetype not provided")

        if self.mimetype.startswith("image/"):
            return Image.open(io.BytesIO(self.data))
        raise ValueError("Not an image file")
