import json
import logging
from pathlib import Path

from core.settings_loader import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_hero_slides():
    # khoi tao file path
    file_path = Path(settings["data"]["processed_dir"]) / "heroSlides.json"
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            hero_slides = json.load(file)
    except json.JSONDecodeError as e:
        logger.error(f"Invalide JSON format {e}")
        return []
    except Exception as e:
        logger.error(f"Failed to load {e}")
        return []
    
    # neu du lieu la dict thi chuyen thanh list chua dict. Vi du: { "title": "Welcome", "subtitle": "to our site" } => [ { "title": "Welcome", "subtitle": "to our site" } ]
    if isinstance(hero_slides, dict):
        hero_slides = [hero_slides]
        
    # kiem tra kieu du lieu co phai la list khong. Vi du: [ { "title": "Welcome", "subtitle": "to our site" }, { "title": "About Us", "subtitle": "Learn more" } ]
    if not isinstance(hero_slides, list):
        logger.error("Hero slides data is not a list")
        return []
    
    # kiem tra danh sach co rong khong. Vi du: []
    if not hero_slides:
        logger.warning("No hero slides found in the data")
        return []
    
    chunks = []  
    
    for idx, slide in enumerate(hero_slides):
        if not isinstance(slide, dict):
            logger.warning(f"Slide at index {idx} is not a dictionary")
            continue
        
        slide_title = slide.get("title", "")
        if not slide_title or not isinstance(slide_title, str):
            logger.warning(f"Slide at index {idx} due to missing or invalid title")
            continue
        
        slide_description = slide.get("description", "")
        if not slide_description or not isinstance(slide_description, str):
            logger.warning(f"Slide at index {idx} due to missing or invalid description")
            continue
        
        slide_id = slide.get("id")
        slide_subtitle = slide.get("subtitle")
        slide_image_url = slide.get("imageUrl", "")
        
        text_parts = [
            f"Hero Slide Title: {slide_title}",
            f"Hero Slide Description: {slide_description}"
        ]
        
        if slide_subtitle and isinstance(slide_subtitle, str):
            text_parts.append(f"Hero Slide Subtitle: {slide_subtitle}")
        
        if slide_image_url:
            text_parts.append("Có hình ảnh banner.")
            
        text = " ".join(text_parts)
        
        chunks.append({
            "text": text,
            "metadata": {
                "type": "hero_slide",
                "id": slide_id,
                "slide_id": slide_id,
                "slide_title": slide_title,
                "slide_subtitle": slide_subtitle,
                "slide_description": slide_description,
                "slide_image_url": slide_image_url,
                "title": slide_title,
                "source": "heroSlides.json"
            }
        })  
    
    if not chunks:
        logger.warning("No valid hero slide chunks were created")
        
    return chunks