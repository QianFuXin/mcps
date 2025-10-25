from mcp.server.fastmcp import FastMCP
from typing import List, Any, Tuple, Optional, Union
from pathlib import Path
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from pdf2image import convert_from_path

# 初始化 FastMCP
mcp = FastMCP("AdvancedFileToolsMCP", port=8003)


# ========== 🖼️ 图片与PDF转换工具 ==========

@mcp.tool()
def picture2pdf(
        image_paths: List[str],
        output_path: str,
        page_size: Tuple[int, int] = (595, 842),
        fit: bool = True
) -> Union[str, dict]:
    """
    将一张或多张图片合并转换为一个PDF文件。

    参数:
    - image_paths: 图片文件的路径列表。
    - output_path: 输出PDF文件的路径。
    - page_size: 页面的尺寸 (宽度, 高度)，单位为pt。默认为A4 (595x842 pt)。
    - fit: 是否等比缩放图片以适应页面，保持图片比例不变。默认为True。

    示例:
    - picture2pdf(["img1.png", "img2.jpg"], "output.pdf")
    - picture2pdf(["photo.jpg"], "custom_size.pdf", page_size=(800, 600), fit=False)
    """
    try:
        pil_images = []
        for img_path_str in image_paths:
            img_path = Path(img_path_str)
            if not img_path.exists():
                return {"error": f"图片文件不存在: {img_path_str}"}

            img = Image.open(img_path).convert("RGB")

            if fit:
                img.thumbnail(page_size, Image.Resampling.LANCZOS)
                background = Image.new("RGB", page_size, (255, 255, 255))
                x_offset = (page_size[0] - img.width) // 2
                y_offset = (page_size[1] - img.height) // 2
                background.paste(img, (x_offset, y_offset))
                pil_images.append(background)
            else:
                # 拉伸以填满页面
                resized_img = img.resize(page_size, Image.Resampling.LANCZOS)
                pil_images.append(resized_img)

        if not pil_images:
            return {"error": "没有提供任何有效的图片进行转换。"}

        pil_images[0].save(
            output_path, save_all=True, append_images=pil_images[1:]
        )
        return f"成功将 {len(pil_images)} 张图片转换为PDF: {output_path}"
    except Exception as e:
        return {"error": f"图片转PDF时发生错误: {e}"}


@mcp.tool()
def pdf2picture(
        pdf_path: str,
        output_dir: str,
        fmt: str = "png",
        dpi: int = 200
) -> Union[List[str], dict]:
    """
    将PDF的每一页转换为指定格式的图片。

    参数:
    - pdf_path: 输入的PDF文件路径。
    - output_dir: 保存输出图片的目录。
    - fmt: 输出图片的格式 (e.g., 'png', 'jpeg')。默认为 'png'。
    - dpi: 渲染图片的DPI（每英寸点数），更高的值会产生更高质量的图片。默认为200。

    示例:
    - pdf2picture("input.pdf", "./output_images")
    - pdf2picture("doc.pdf", "./jpeg_pages", fmt="jpeg", dpi=300)
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        return {"error": f"PDF文件不存在: {pdf_path}"}

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        images = convert_from_path(pdf_path, dpi=dpi, fmt=fmt)
        saved_files = []
        for i, image in enumerate(images):
            image_file = output_path / f"page_{i + 1}.{fmt.lower()}"
            image.save(image_file)
            saved_files.append(str(image_file))
        return saved_files
    except Exception as e:
        return {"error": f"PDF转图片时发生错误: {e}"}


# ========== 🛠️ PDF 编辑与操作工具 ==========

@mcp.tool()
def pdf_merge(pdf_files: List[str], output_path: str) -> Union[str, dict]:
    """
    将多个PDF文件合并成一个单一的PDF文件。

    参数:
    - pdf_files: 要合并的PDF文件路径列表。
    - output_path: 合并后输出的PDF文件路径。

    示例:
    - pdf_merge(["part1.pdf", "part2.pdf"], "merged_document.pdf")
    """
    merger = PdfMerger()
    try:
        for pdf_path in pdf_files:
            if not Path(pdf_path).exists():
                merger.close()
                return {"error": f"待合并的文件不存在: {pdf_path}"}
            merger.append(pdf_path)
        merger.write(output_path)
        merger.close()
        return f"成功将 {len(pdf_files)} 个PDF文件合并为: {output_path}"
    except Exception as e:
        return {"error": f"合并PDF时发生错误: {e}"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
