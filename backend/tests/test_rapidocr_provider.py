import sys
import types

from PIL import Image

from app.schemas.review import OCRConfig
from app.services.ocr_providers.rapidocr_provider import RapidOCROCRProvider


def test_rapidocr_provider_joins_results(monkeypatch) -> None:
    class FakeRapidOCR:
        def __call__(self, image_bytes):
            assert image_bytes
            return (
                [
                    [None, "第一章 叶序", "0.99"],
                    [None, "考试重点", "0.98"],
                ],
                [0.1, 0.1, 0.1],
            )

    fake_module = types.SimpleNamespace(RapidOCR=lambda: FakeRapidOCR())
    monkeypatch.setitem(sys.modules, "rapidocr_onnxruntime", fake_module)

    text = RapidOCROCRProvider().extract_text(
        Image.new("RGB", (20, 20), "white"),
        OCRConfig(provider="rapidocr"),
    )

    assert text == "第一章 叶序\n考试重点"
