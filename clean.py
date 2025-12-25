import fitz  # PyMuPDF
import cv2
import numpy as np
import os
import re

# ================= 配置区域 (只需改这里，输入文件路径) =================

# 输入和输出文件名
INPUT_FILE = "你的文件名.pdf"
OUTPUT_FILE = "去除水印_你的文件名.pdf"

# --- 模式选择 ---
# "VISUAL" = 强力视觉模式 (推荐！专治顽固水印，正文变图片，但在打印/阅读时效果完美)
# "TEXT"   = 文本删除模式 (仅尝试删除特定文字，保留正文可复制，但对图形水印无效)
MODE = "VISUAL" 

# --- [VISUAL 模式专用] 保留颜色配置 ---
# 默认必定保留黑色 (正文)。这里可以添加你想要保留的其他颜色标题。
# 可选: 'red', 'blue', 'green', 'yellow' (支持组合，如 ['red', 'blue'])
KEEP_COLORS = ['red'] 

# --- [TEXT 模式专用] 要删除的关键词 ---
# 支持正则表达式，不区分大小写
REMOVE_KEYWORDS = [
    r"TIENG PHAP", 
    r"PIMSLEUR", 
    r"CONFIDENTIAL", 
    r"DO NOT COPY"
]

# ==========================================================

def get_color_mask(hsv_img, color_name):
    """根据颜色名称生成掩膜"""
    masks = []
    
    # 定义常见颜色的 HSV 范围 (OpenCV H:0-180, S:0-255, V:0-255)
    color_ranges = {
        'red': [
            (np.array([0, 50, 50]), np.array([10, 255, 255])),
            (np.array([170, 50, 50]), np.array([180, 255, 255]))
        ],
        'blue': [
            (np.array([100, 50, 50]), np.array([130, 255, 255]))
        ],
        'green': [
            (np.array([35, 50, 50]), np.array([85, 255, 255]))
        ],
        'yellow': [
            (np.array([20, 50, 50]), np.array([35, 255, 255]))
        ]
    }
    
    if color_name in color_ranges:
        for (lower, upper) in color_ranges[color_name]:
            masks.append(cv2.inRange(hsv_img, lower, upper))
    
    # 合并该颜色的所有掩膜
    final_mask = masks[0] if masks else np.zeros(hsv_img.shape[:2], dtype=np.uint8)
    for m in masks[1:]:
        final_mask = final_mask | m
    return final_mask

def visual_clean_mode(doc, output_path):
    """强力视觉模式：基于颜色过滤"""
    new_doc = fitz.open()
    print(f"🚀 启动 [VISUAL] 模式，正在处理 {len(doc)} 页...")
    print(f"🎨 保留策略: 黑色正文 + {KEEP_COLORS}")

    for i, page in enumerate(doc):
        # 1. 渲染为高清图片 (300 DPI)
        pix = page.get_pixmap(dpi=300)
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        
        # RGB 转 BGR (OpenCV) 再转 HSV
        if pix.n == 4:
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        else:
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        # 2. 提取黑色 (正文核心)
        # H任意, S任意, V(亮度) 0-110 (允许深灰，但不允许浅灰水印)
        mask_black = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 110]))
        
        # 3. 提取额外保留的颜色
        mask_extra = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for color_name in KEEP_COLORS:
            mask_extra = mask_extra | get_color_mask(hsv, color_name)

        # 4. 合并所有要保留的区域
        mask_final = mask_black | mask_extra

        # 5. 重建白底图片
        result_img = np.full_like(img_bgr, 255) # 全白
        result_img[mask_final > 0] = img_bgr[mask_final > 0] # 填入保留像素

        # 6. 存回 PDF
        temp_img = f"temp_p{i}.jpg"
        # 质量 85 以平衡体积
        cv2.imwrite(temp_img, result_img, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, filename=temp_img)
        os.remove(temp_img)
        
        if (i+1) % 5 == 0:
            print(f"   进度: {i+1} / {len(doc)} 页...")

    new_doc.save(output_path, garbage=4, deflate=True)

def text_clean_mode(doc, output_path):
    """文本删除模式：基于关键词匹配"""
    print(f"🚀 启动 [TEXT] 模式，正在扫描关键词: {REMOVE_KEYWORDS}")
    
    removed_count = 0
    for page in doc:
        # 查找所有匹配的关键词
        for keyword in REMOVE_KEYWORDS:
            text_instances = page.search_for(keyword)
            for inst in text_instances:
                page.add_redact_annot(inst) # 标记删除
                removed_count += 1
        
        # 应用删除
        page.apply_redactions()
    
    doc.save(output_path, garbage=4, deflate=True)
    print(f"✅ 处理完成，共移除 {removed_count} 处匹配文本。")

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 错误: 找不到文件 '{INPUT_FILE}'。请在代码顶部修改 INPUT_FILE。")
    else:
        try:
            doc_obj = fitz.open(INPUT_FILE)
            if MODE == "VISUAL":
                visual_clean_mode(doc_obj, OUTPUT_FILE)
            elif MODE == "TEXT":
                text_clean_mode(doc_obj, OUTPUT_FILE)
            else:
                print("未知的 MODE 配置，请检查代码。")
            
            doc_obj.close()
            print(f"\n✨ 任务结束！文件已生成: {OUTPUT_FILE}")
        except Exception as e:
            print(f"发生错误: {str(e)}")