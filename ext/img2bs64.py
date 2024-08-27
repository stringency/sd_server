import base64

# 图片路径
image_path = "00004.png"  # 替换为你的图片路径

# 读取图片并转换为base64编码
with open(image_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

# 输出base64编码字符串
print(encoded_string)
# 保存为txt文件
with open("base64_code.txt", "w") as file:
    file.write(encoded_string)
