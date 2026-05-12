from PIL import Image, ImageDraw, ImageFont
import httpx
from io import BytesIO


def render_badge(profile_img_url: str) -> BytesIO:

    canvas = Image.new("RGB", (1080, 1080), "black")
    draw = ImageDraw.Draw(canvas)

    font = ImageFont.load_default()

    # Heading
    draw.text((420, 100), "Async Engine", fill="white", font=font)

    # Profile image
    try:
        res = httpx.get(profile_img_url, timeout=5)
        res.raise_for_status()
        profile = Image.open(BytesIO(res.content)).convert("RGB")
        profile = profile.resize((400, 400))
        canvas.paste(profile, (340, 250))
    except Exception as e:
        raise RuntimeError(f"Failed to download or process profile image: {str(e)}")

    # Footer
    draw.text(
        (120, 750),
        "sample badge generated. Base proof of concept. Awaiting further dev",
        fill="white",
        font=font
    )

    buffer = BytesIO()
    canvas.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer