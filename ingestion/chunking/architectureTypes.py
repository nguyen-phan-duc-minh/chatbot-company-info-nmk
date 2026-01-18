import json
import logging
from pathlib import Path

from core.settings_loader import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_architecture_types():
    # Khai bao file path
    file_path = Path(settings["data"]["processed_dir"]) / "architectureTypes.json"
    
    # Kiem tra file ton tai
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []
    
    # Doc du lieu tu file JSON,
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            architecture_types = json.load(f)
    # neu file json khong hop le thi log loi
    except json.JSONDecodeError as e: # bat loi khi doc file json
        logger.error(f"Invalid JSON format {e}")
        return []
    # neu khong co du lieu thi log loi
    except Exception as e:
        logger.error(f"Failed to load {e}")
        return []
    
    if isinstance(architecture_types, dict): # neu du lieu la dict thi chuyen thanh list chua dict. Vi du: { "name": "Modern" } => [ { "name": "Modern" } ]
        architecture_types = [architecture_types]
    
    if not isinstance(architecture_types, list): # kiem tra kieu du lieu co phai la list khong. Vi du: [ { "name": "Modern" }, { "name": "Contemporary" } ]
        logger.error("Architecture types data is not a list")
        return []

    if not architecture_types: # kiem tra danh sach co rong khong. VI du: []
        logger.warning("No architecture types found in the data")
        return []
    
    chunks = [] # danh sach luu cac doan van ban
    
    for idx, architecture_type in enumerate(architecture_types):
        if not isinstance(architecture_type, dict): # kiem tra kieu du lieu co phai la dict khong. Vi du: { "name": "Modern" }
            logger.warning(f"Invalid architecture type at index {idx}: expected a dictionary")
            continue
        
        architecture_id = architecture_type.get("id") # lay id loai kien truc
        architecture_slug = architecture_type.get("slug", "") # lay slug loai kien truc
        architecture_name = architecture_type.get("name", "") # lay ten loai kien truc
        if not architecture_name or not isinstance(architecture_name, str): # kiem tra ten loai kien truc co hop le khong. Vi du: "Modern"
            logger.warning(f"Architecture type at index {idx} due to missing or invalid name")
            continue
            
        text = f'Tên loại kiến trúc: {architecture_name}.' # tao doan van ban voi ten loai kien truc
        
        chunks.append ({ 
            "text": text,
            "metadata": {
                "type": "architecture_type",
                "architecture_type_id": architecture_id,
                "architecture_type_slug": architecture_slug,
                "architecture_type_name": architecture_name,
                "source": "architectureTypes.json"
            }
        })
    if not chunks:
        logger.warning("No valid architecture type chunks were created")
            
    return chunks