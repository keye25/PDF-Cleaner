# PDF-Cleaner
PDF去水印工具

此项目基于 [PDF-Watermark-Removal](https://github.com/StuHude/PDF-Watermark-Removal) 修改。
针对 app.py 无法去除的水印类型，我添加了 clean.py 脚本用于处理特定类型的水印（仅支持代码调用），更加强力有效。

This project is based on [PDF-Watermark-Removal](https://github.com/StuHude/PDF-Watermark-Removal) 
I added the clean.py script to handle specific types of watermarks that app.py cannot remove (supports code execution only).

# 以下说明来自 PDF-Watermark-Removal 原readme，


## **需要的库：**

pip install opencv-python

pip install fitz

pip install fpdf

pip install flask

还有一些常见的PIL、numpy等等

# 若调用app.py请参考以下方式

## **如何运行：**

安装所需的库之后，运行app.py，会给出网址（运行在本地），点击进入即可。

在网站中上传pdf文件，点击去除水印，下载去除后的pdf文件

## **原理：**

将pdf转为多张图片，用cv方法去除每张图片水印，再转回pdf

可以自行设置转换图片的分辨率，默认为300DPI，分辨率越高，去除水印后下载的pdf文件和上传的源文件之间的清晰度差距越小（失真越小）。

如果不是一页密密麻麻很多小字的pdf，不需要很高DPI即可保证处理后的pdf文件与原文件清晰度一致，300DPI完全够用。

## **注意：**

处理pdf文件时间=0.8s * 文件页数（有时间加个进度条）

基本只针对灰色（暗色）水印

pdf转换的图片默认设置300DPI，基本满足需求，可能有部分pdf去除水印后会清晰度损失。计划之后再提供自行设置分辨率功能。

## 另：单图像去除水印
运行UI1.html(如Open In Browser)，即可在网站中去除图片水印、对比处理前后图像、下载处理后图像

### 图像去除水印网页↓↓↓

![PS_%ROHKWH$CSV4X1_Z6QRY](https://github.com/StuHude/PDF-Watermark-Removal/assets/89311278/3db93765-0b97-4cfc-a9d4-3fceb2ba68e7)


# 若调用app.py方式无效，调用clean.py
两种模式可选，配置对应参数
1. "VISUAL" = 强力视觉模式 (推荐！专治顽固水印，正文变图片，但在打印/阅读时效果完美)
2. "TEXT"   = 文本删除模式 (仅尝试删除特定文字，保留正文可复制，但对图形水印无效)



