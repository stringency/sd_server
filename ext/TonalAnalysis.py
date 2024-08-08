from PIL import Image
import numpy as np
from collections import Counter
import webcolors

def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def get_color_name(rgb):
    try:
        color_name = webcolors.rgb_to_name(rgb)
    except ValueError:
        color_name = closest_color(rgb)
    return color_name

def get_dominant_colors(image_path, num_colors=5):
    # 打开图像文件
    img = Image.open(image_path)

    # 将图像转换为RGB格式
    img = img.convert('RGB')

    # 获取图像的像素值
    pixels = np.array(img)

    # 将二维数组展开为一维
    pixels = pixels.reshape(-1, 3)

    # 使用Counter计算每种颜色出现的频率
    color_counts = Counter(map(tuple, pixels))

    # 获取按频率排序的颜色列表
    dominant_colors = color_counts.most_common(num_colors)

    return dominant_colors

# 示例用法
image_path = r"F:\GithubProject\stable-diffusion-webui\outputs\img2img-images\2024-07-29\1722223571890.jpg"  # 替换为你的图像路径
dominant_colors = get_dominant_colors(image_path)

print("主色调排序列表：")
for color, count in dominant_colors:
    color_name = get_color_name(color)
    print(f"颜色: {color}, 出现次数: {count}, 名称: {color_name}")
