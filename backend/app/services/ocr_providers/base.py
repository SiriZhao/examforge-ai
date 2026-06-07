from abc import ABC, abstractmethod

from PIL import Image

from app.schemas.review import OCRConfig


class BaseOCRProvider(ABC):
    name: str

    @abstractmethod
    def extract_text(self, image: Image.Image, config: OCRConfig) -> str:
        raise NotImplementedError
