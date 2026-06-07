import base64

from PIL import Image

from app.schemas.review import OCRConfig
from app.services.ocr_providers.base import BaseOCRProvider
from app.services.ocr_providers.utils import image_to_bytes


class BaiduOCROCRProvider(BaseOCRProvider):
    name = "baidu_ocr"

    def extract_text(self, image: Image.Image, config: OCRConfig) -> str:
        import httpx

        if not config.api_key or not config.secret_key:
            raise RuntimeError("百度 OCR 需要 API Key 和 Secret Key。")

        try:
            token_response = httpx.post(
                "https://aip.baidubce.com/oauth/2.0/token",
                params={
                    "grant_type": "client_credentials",
                    "client_id": config.api_key,
                    "client_secret": config.secret_key,
                },
                timeout=30,
            )
            token_response.raise_for_status()
            access_token = token_response.json().get("access_token")
        except httpx.HTTPError as exc:
            raise RuntimeError("百度 OCR token 请求失败。") from exc

        if not access_token:
            raise RuntimeError("百度 OCR 未返回 access_token。")

        image_base64 = base64.b64encode(image_to_bytes(image)).decode("utf-8")
        try:
            ocr_response = httpx.post(
                "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic",
                params={"access_token": access_token},
                data={"image": image_base64, "language_type": "CHN_ENG"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=60,
            )
            ocr_response.raise_for_status()
            data = ocr_response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("百度 OCR 请求失败。") from exc
        except ValueError as exc:
            raise RuntimeError("百度 OCR 返回了无效 JSON。") from exc

        if "error_code" in data:
            raise RuntimeError(f"百度 OCR 失败：{data.get('error_msg', '未知错误')}")

        return "\n".join(item.get("words", "") for item in data.get("words_result", [])).strip()
