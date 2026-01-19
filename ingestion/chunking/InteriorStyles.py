import json
import logging
from pathlib import Path

from core.settings_loader import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_interior_styles():
    file_path = Path(settings["data"]["processed_dir"]) / "interiorStyles.json"
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []
    
    try: 
        with open(file_path, 'r', encoding='utf-8') as file:
            interior_styles = json.load(file)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format {e}")
        return []
    except Exception as e:
        logger.error(f"Failed to load {e}")
        return []
    
    # Chuyen tu dict sang list neu can thiet
    if isinstance(interior_styles, dict):
        interior_styles = [interior_styles]
        
    # kiem tra xem co phai list khong
    if not isinstance(interior_styles, list):
        logger.error("Interior styles data is not a list")
        return []
    
    if not interior_styles:
        logger.warning("No interior styles found in the file")
        return []
    
    chunks = []
    
    for idx, interior_style in enumerate(interior_styles):
        if not isinstance(interior_style, dict):
            logger.warning(f"Interior style at index {idx} is not a dictionary")
            continue
        
        interior_id = interior_style.get("id")
        interior_slug = interior_style.get("slug", "")
        interior_name = interior_style.get("name", "")
        interior_description = interior_style.get("description", "")
        interior_image_url = interior_style.get("imageUrl", "")
        
        if not interior_name or not isinstance(interior_name, str):
            logger.warning(f"Interior style at index {idx} due to missing or invalid name")
            continue
        
        # Build rich text content
        text_parts = [f'Phong cách nội thất: {interior_name}']
        
        if interior_description and interior_description.strip():
            text_parts.append(f'Mô tả: {interior_description}')
        else:
            text_parts.append(f'Đây là một trong những phong cách nội thất phổ biến của NMK Architecture.')
        
        if interior_image_url:
            text_parts.append(f'Hình ảnh tham khảo có sẵn.')
        
        text = ' '.join(text_parts)
        
        chunks.append({
            "text": text,
            "metadata": {
                "type": "interior_style",
                "interior_style_id": interior_id,
                "interior_style_slug": interior_slug,
                "interior_style_name": interior_name,
                "interior_style_description": interior_description or "",
                "interior_style_image_url": interior_image_url,
                "source": "interiorStyles.json"
            }
        })
        
    if not chunks:
        logger.warning("No valid interior style chunks were created")
        
    return chunks