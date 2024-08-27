import re
import random
import argparse
import base64
from io import BytesIO
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def replace_space_between_first_two_words(text):
    # 匹配前两个单词及它们之间的空格
    match = re.search(r'(\b\w+\b)\s+(\b\w+\b)', text)
    if match:
        # 替换匹配到的空格为 \n
        replaced_text = re.sub(r'\s+', '\\n', match.group(0))
        # 返回替换后的字符串
        return replaced_text
    else:
        return "No two words found."

def calculate_variance_with_color(pixels, color):
    """
    计算与给定颜色的方差
    """
    # 将像素数组和颜色转换为numpy数组以便计算
    pixels = np.array(pixels)
    color = np.array(color)
    # 计算每个像素与给定颜色之间的平方差
    variance = np.mean(np.sum((pixels - color) ** 2, axis=1))
    return variance

def get_optimal_contrast_color(img, areas):
    """
    比较区域内像素与黑色和白色的方差，选择方差大的颜色
    """
    # 提取区域内的像素
    pixels = []
    for area in areas:
        pixels.extend([img.getpixel((x, y)) for x in range(area[0], area[2]) for y in range(area[1], area[3])])
    
    if not pixels:
        return "No pixels in area"

    # 计算与黑色和白色的方差
    black_variance = calculate_variance_with_color(pixels, (0, 0, 0))
    white_variance = calculate_variance_with_color(pixels, (255, 255, 255))

    # 选择方差较大的颜色
    if black_variance > white_variance:
        return "black"
    else:
        return "white"

def draw_vertical_text(draw, text, font_path, font_size, position, gap, fill):
    # 加载字体
    font = ImageFont.truetype(font_path, font_size)

    # text_color = "black"

    # 竖排文字
    x = position[0]  # 设置文字的水平开始位置
    y = position[1]  # 设置文字的垂直开始位置
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        y += font.getsize(char)[1]-gap  # 更新y坐标，向下移动


def insert_newlines_in_chinese(text):
    # 使用正则表达式找到所有中文字符
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    
    # 取前四个中文字符
    first_four_chars = chinese_chars[:4]
    
    # 将这四个字符组合为字符串
    combined_chars = ''.join(first_four_chars)
    
    # 在每两个字符后插入换行符
    formatted_string = '\n'.join([combined_chars[i:i+2] for i in range(0, len(combined_chars), 2)])
    
    return formatted_string

def draw_multiline_text_with_spacing(draw, text, font_path, font_size, position, gap, fill, line_spacing=10, char_spacing=10):
    x_start, y_start = position
    font = ImageFont.truetype(font_path, font_size)
    lines = text.split('\n')
    y = y_start
    for line in lines:
        x = x_start
        # 逐字符绘制，添加字间距
        for char in line:
            draw.text((x, y), char, font=font, fill=(0, 0, 0))
            x += font.getsize(char)[0] + char_spacing
        y += font.getsize(line)[1] + line_spacing  # Move y down for the next line

def center_text(draw, text, font_path, font_size, position, gap, fill):
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = draw.textsize(text, font=font)
    text_width += len(text)*gap

    # 计算左上角坐标
    top_left_x = position[0] - text_width // 2
    top_left_y = position[1] - text_height // 2
    for char in text:
        draw.text((top_left_x, top_left_y), char, font=font, fill=(0, 0, 0))
        text_width, text_height = draw.textsize(char, font=font)
        top_left_x += gap
        top_left_x += text_width



def rotate_text(image, draw, text, font_path, font_size, position, gap, fill):
    font = ImageFont.truetype(font_path, font_size)

    # 旋转文字图像
    rotated_text_image = image.rotate(90, expand=1)
    text_draw = ImageDraw.Draw(rotated_text_image)
    text_draw.text(position, text, font=font, fill='black')
    image = rotated_text_image.rotate(-90, expand=1)
    draw = ImageDraw.Draw(rotated_text_image)
    return image, draw


def add_black_text():
    # 替换生成图片的地址，生成白底黑字，注释这行代码
    image = Image.new("RGB", (768, 1024), (255, 255, 255))
    # image = Image.open("outputs/txt2img-images/2024-08-14/00001-1164290984.png")

    draw = ImageDraw.Draw(image)

    # style_index = random.choice([1, 2, 3, 4])
    style_index = 1

    if style_index == 1:
        eng = "Limited Edition"
        eng = replace_space_between_first_two_words(eng)
        # Style 1
        texts = [
            {"text": "限量周边", "position": (560, 55), "font_size": 150, "font_path": "assets/Font/方正粗黑宋简体.ttf", "font_direction": "vertical", "gap":0},
            {"text": "粉丝独家，抢购从速", "position": (490, 70), "font_size": 50, "font_path": "assets/Font/方正粗黑宋简体.ttf", "font_direction": "vertical", "gap":0},
            {"text": "01", "position": (55, 60), "font_size": 60, "font_path": "assets/Font/BELL.TTF", "font_direction": "Horizontal", "gap":0},
            {"text": "动漫热潮", "position": (50, 130), "font_size": 50, "font_path": "assets/Font/方正粗黑宋简体.ttf", "font_direction": "Horizontal", "gap":0},
            {"text": "02", "position": (55, 340), "font_size": 60, "font_path": "assets/Font/BELL.TTF", "font_direction": "Horizontal", "gap":0},
            {"text": "抢购不停", "position": (50, 410), "font_size": 50, "font_path": "assets/Font/方正粗黑宋简体.ttf", "font_direction": "Horizontal", "gap":0},
            {"text": eng, "position": (50, 780), "font_size": 100, "font_path": "assets/Font/tt1106m_.ttf", "font_direction": "Horizontal", "gap":0},
        ]
    elif style_index == 2:
        main_title = "限量周边"
        main_title = insert_newlines_in_chinese(main_title)
        eng = "Limited Edition"
        eng = replace_space_between_first_two_words(eng)
        texts = [
            {"text": main_title, "position": (60, 60), "font_size": 175, "font_path": "assets/Font/思源黑体SourceHanSansCN-Medium.ttf", "font_direction": "Style2", "gap":0},
            {"text": "畅游二次元", "position": (70, 450), "font_size": 50, "font_path": "assets/Font/方正粗黑宋简体.ttf", "font_direction": "Horizontal", "gap":0},
            # {"text": "01", "position": (55, 60), "font_size": 60, "font_path": "assets/Font/BELL.TTF", "font_direction": "Horizontal", "gap":0},
            {"text": "粉丝独家，抢购从速", "position": (70, 900), "font_size": 50, "font_path": "assets/Font/思源黑体SourceHanSansCN-Medium.ttf", "font_direction": "Horizontal", "gap":0},
            # {"text": "02", "position": (55, 340), "font_size": 60, "font_path": "assets/Font/BELL.TTF", "font_direction": "Horizontal", "gap":0},
            # {"text": subject02, "position": (50, 410), "font_size": 50, "font_path": "assets/Font/方正粗黑宋简体.ttf", "font_direction": "Horizontal", "gap":0},
            {"text": eng, "position": (65, 30), "font_size": 100, "font_path": "assets/Font/tt0246m_.ttf", "font_direction": "Rotate", "gap":0},
        ]
    elif style_index == 3:
        texts = [
            {"text": f"动漫奇幻乐园", "position": (385, 120), "font_size": 100, "font_path": "assets/Font/simsun.ttc", "font_direction": "Center", "gap":20},
            {"text": f"畅游二次元", "position": (385, 260), "font_size": 50, "font_path": "assets/Font/方正粗黑宋简体.ttf", "font_direction": "Center", "gap":5},
            {"text": "99", "position": (385, 900), "font_size": 150, "font_path": "assets/Font/arial.ttf", "font_direction": "Center", "gap":0},
            {"text": "发现独特周边", "position": (384, 800), "font_size": 60, "font_path": "assets/Font/方正粗黑宋简体.ttf", "font_direction": "Center", "gap":0},
            # # {"text": "02", "position": (55, 340), "font_size": 60, "font_path": "assets/Font/BELL.TTF", "font_direction": "Horizontal", "gap":0},
            # # {"text": subject02, "position": (50, 410), "font_size": 50, "font_path": "assets/Font/方正粗黑宋简体.ttf", "font_direction": "Horizontal", "gap":0},
            {"text": "Limited Edition", "position": (385, 320), "font_size": 70, "font_path": "assets/Font/ariblk.ttf", "font_direction": "Center", "gap":0},
        ]
    else:
        texts = [
            {"text": f"Connect with\nFans", "position": (55, 60), "font_size": 75, "font_path": "assets/Font/STENCIL.TTF", "font_direction": "Horizontal", "gap":0},
            {"text": f"New\nExclusives", "position": (55, 170), "font_size": 100, "font_path": "assets/Font/ariblk.ttf", "font_direction": "Horizontal", "gap":0},
            {"text": f"动漫奇幻", "position": (395, 850), "font_size": 160, "font_path": "assets/Font/思源黑体SourceHanSansCN-Medium.ttf", "font_direction": "Center", "gap":20},
            {"text": f"Dive into the World of Anime", "position": (384, 980), "font_size": 45, "font_path": "assets/Font/ariblk.ttf", "font_direction": "Center", "gap":0},
        ]


    # Draw text
    for text_detail in texts:
        font = ImageFont.truetype(text_detail["font_path"], text_detail["font_size"])
        if text_detail["font_direction"] == "Horizontal":
            draw.text(text_detail["position"], text_detail["text"], font=font, fill='black')
        elif text_detail["font_direction"] == "Center":
            center_text(draw, text_detail["text"], text_detail["font_path"], text_detail["font_size"], text_detail["position"], text_detail["gap"], fill='black')
        elif text_detail["font_direction"] == "Style2":
            draw_multiline_text_with_spacing(draw, text_detail["text"], text_detail["font_path"], text_detail["font_size"], text_detail["position"], text_detail["gap"], fill='black')
        elif text_detail["font_direction"] == "Rotate":
            image, draw = rotate_text(image, draw, text_detail["text"], text_detail["font_path"], text_detail["font_size"], text_detail["position"], text_detail["gap"], fill='black')
        else:
            draw_vertical_text(draw, text_detail["text"], text_detail["font_path"], text_detail["font_size"], text_detail["position"], text_detail["gap"], fill='black')
    
    # # Save image
    # image.save(output_path)
    # print(style_index)
    # Save image to a buffer
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)

    # Encode image to base64
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    # Save base64 image to the file if needed
    # with open(output_path, "wb") as f:
    #     f.write(base64.b64decode(img_base64))

    # 将整数转换为字节字符串
    byte_string = str(style_index).encode('utf-8')
    # 将字节字符串编码为 Base64 字符串
    encoded = base64.b64encode(byte_string).decode('utf-8')
    
    return img_base64, encoded

# if __name__ == '__main__':
#
#     img, index = add_black_text()
#
#     print(img)
#     print("index:",index)