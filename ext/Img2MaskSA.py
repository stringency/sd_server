import torch
from PIL import Image,ImageOps
import base64
from io import BytesIO
import numpy as np
from segment_anything import SamPredictor, sam_model_registry

# 加载 Segment Anything 模型
sam_checkpoint = "assets/models/sam_vit_h.pth"
model_type = "vit_h"  # 选择模型类型

device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)

# 加载模型
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)
predictor = SamPredictor(sam)


def generate_mask_SA(base64_image):
    # 解码Base64图像
    image_data = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_data)).convert("RGB")

    # 转换为 NumPy 数组
    image_np = np.array(image)

    # 设置图像到预测器
    predictor.set_image(image_np)

    # 使用 SAM 进行分割
    masks, _, _ = predictor.predict(point_coords=None, point_labels=None, multimask_output=False)

    # 提取第一个掩码
    mask = masks[0]

    # 将掩码转换为 uint8 并乘以 255 以获得白色前景
    mask = (mask * 255).astype(np.uint8)

    # 将蒙版转换为PIL图像
    mask_image = Image.fromarray(mask)

    # 反转蒙版图像，使产品为白色，背景为黑色
    mask_image = ImageOps.invert(mask_image)

    # 显示蒙版图像
    mask_image.show()

    # 将蒙版图像转换回Base64
    buffered = BytesIO()
    mask_image.save(buffered, format="PNG")
    mask_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return mask_base64


# 示例：传入Base64编码的图像
# with open("base64_code.txt", "r") as file:
#     input_base64_image = file.read()
#
# mask_base64_image = generate_mask(input_base64_image)
# print(mask_base64_image)
