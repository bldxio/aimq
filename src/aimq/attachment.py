import io
import typing
from typing import Any

import filetype
import humanize
from PIL import Image
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, computed_field


class Attachment(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: bytes = Field(..., description="The bytes of the attachment", exclude=True)

    _mimetype: str = PrivateAttr(default="application/octet-stream")
    _extension: str | None = PrivateAttr(default=None)

    @computed_field
    @property
    def mimetype(self) -> str:
        return self._mimetype

    @computed_field
    @property
    def extension(self) -> str | None:
        return self._extension

    def model_post_init(self, __context: Any) -> None:
        kind = filetype.guess(self.data)
        if kind:
            self._mimetype = kind.mime
            self._extension = kind.extension

    @computed_field
    def size(self) -> str:
        return humanize.naturalsize(len(self.data))

    def get(self, key: str, default=None):
        if hasattr(self, key):
            return getattr(self, key, default)
        return default

    def __repr_args__(self) -> typing.Iterable[tuple[str | None, Any]]:
        attrs = self.model_dump(exclude={"data", "_mimetype", "_extension"}).items()
        return [(a, v) for a, v in attrs if v is not None]

    def to_file(self):
        if not self.data or not self.mimetype:
            raise ValueError("Data or mimetype not provided")

        if self.mimetype.startswith("image/"):
            return Image.open(io.BytesIO(self.data))
        raise ValueError("Not an image file")
