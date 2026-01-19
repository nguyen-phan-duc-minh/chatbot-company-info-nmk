import json
import logging
from pathlib import Path

from core.settings_loader import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_projects():
    file_path = Path(settings["data"]["processed_dir"]) / "projects.json"
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            projects = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format {e}")
        return []
    except Exception as e:
        logger.error(f"Failed to load {e}")
        return []   
    
    if isinstance(projects, dict):
        projects = [projects]
        
    if not isinstance(projects, list):
        logger.error("Projects data is not a list")
        return []
    
    if not projects:
        logger.warning("No projects found in the file")
        return []
    
    chunks = []
    
    for idx, project in enumerate(projects):
        if not isinstance(project, dict):
            logger.warning(f"Project at index {idx} is not a dict")
            continue
        
        project_id = project.get("id")
        project_name = project.get("title", "")
        if not project_name or not isinstance(project_name, str):
            logger.warning(f"Project at index {idx} has invalid or missing title")
            continue
        
        project_slug = project.get("slug", "")
        project_investor = project.get("investor", "")
        project_location = project.get("location", "")
        project_description = project.get("description", "")
        project_thumbnail_url = project.get("thumbnailUrl", "")
        project_completed_date = project.get("completedDate", "")
        project_area = project.get("area")
        if not isinstance(project_area, (int, float)):
            project_area = None
        
        project_view_count = project.get("viewCount")
        if not isinstance(project_view_count, int):
            project_view_count = 0
            
        project_published_at = project.get("publishedAt")
        
        category = project.get("category", {})
        if not isinstance(category, dict):
            logger.warning(f"Project at index {idx} has invalid category")
            continue
        
        project_category_id = category.get("id")
        project_category_name = category.get("name", "")
        if not project_category_name or not isinstance(project_category_name, str):
            logger.warning(f"Project at index {idx} has invalid or missing category name")
            continue
        
        project_category_slug = category.get("slug")
        
        interior = project.get("interiorStyle", {})
        if not isinstance(interior, dict):
            logger.warning(f"Project at index {idx} has invalid interior")
            continue
        
        project_interior_id = interior.get("id")
        project_interior_name = interior.get("name", "")
        if not project_interior_name or not isinstance(project_interior_name, str):
            logger.warning(f"Project at index {idx} has invalid or missing interior name")
            continue
        
        project_interior_slug = interior.get("slug")
        
        # Build rich text content
        text_parts = [f"Dự án: {project_name}"]
        
        if project_description and project_description.strip():
            text_parts.append(f"Mô tả: {project_description}")
        
        text_parts.append(f"Danh mục: {project_category_name}")
        text_parts.append(f"Phong cách nội thất: {project_interior_name}")
        
        if project_location:
            text_parts.append(f"Địa điểm: {project_location}")
        
        if project_investor:
            text_parts.append(f"Chủ đầu tư: {project_investor}")
        
        if project_area:
            text_parts.append(f"Diện tích: {project_area} m²")
        
        if project_completed_date:
            text_parts.append(f"Hoàn thành: {project_completed_date[:10]}")
        
        if project_thumbnail_url:
            text_parts.append("Có hình ảnh tham khảo.")
        
        text = " ".join(text_parts)
        
        chunks.append({
            "text": text,
            "metadata": {
                "type": "project",
                "project_id": project_id,
                "project_slug": project_slug,
                "project_name": project_name,
                "project_description": project_description or "",
                "project_thumbnail_url": project_thumbnail_url,
                "project_image_url": project_thumbnail_url, 
                "project_view_count": project_view_count,
                "project_published_at": project_published_at,
                "project_area": project_area,
                "project_investor": project_investor,
                "project_location": project_location,
                "project_completed_date": project_completed_date,
                "project_category_id": project_category_id,
                "project_category_name": project_category_name,
                "project_category_slug": project_category_slug,
                "project_interior_id": project_interior_id,
                "project_interior_name": project_interior_name,
                "project_interior_slug": project_interior_slug,
                "source": "projects.json"
            }
        })
        
    if not chunks:
        logger.warning("No valid project chunks were created")
        
    return chunks