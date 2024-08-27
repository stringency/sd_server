from PIL import Image, ImageOps, ImageFilter
import base64
from io import BytesIO


def generate_mask_PIL(base64_image):
    # 解码Base64图像
    image_data = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_data)).convert("RGB")

    # 转换为灰度图像
    gray_image = ImageOps.grayscale(image)

    # 应用轻微模糊处理，以减少噪声并平滑细节
    blurred_image = gray_image.filter(ImageFilter.GaussianBlur(2))

    # 自动生成蒙版图像（假设背景是白色）
    threshold = 250  # 降低阈值，以捕捉更多的细节
    mask = blurred_image.point(lambda p: p > threshold and 255)
    mask = ImageOps.invert(mask)  # 将背景变黑，前景变白

    # 提高对比度，确保细节完整
    mask = ImageOps.autocontrast(mask)

    # mask.show()

    # 将蒙版图像转换回Base64
    buffered = BytesIO()
    mask.save(buffered, format="PNG")
    mask_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return mask_base64


# 示例：传入Base64编码的图像
# with open("base64_code.txt", "r") as file:
#     input_base64_image = file.read()
# mask_base64_image = generate_mask(input_base64_image)
# print(mask_base64_image)
