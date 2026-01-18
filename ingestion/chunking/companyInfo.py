import json
import logging
from pathlib import Path

from core.settings_loader import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_company_info():
    # khai bao file path
    file_path = Path(settings["data"]["processed_dir"]) / "companyInfo.json"
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []
    
    # doc du lieu tu file json
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            company_info =json.load(f)
    # neu file json khong hop le thi log loi. Vi du: , cuois cau, thieu ngoac,....
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format {e}")
        return []
    # neu khong co du lieu thi log loi
    except Exception as e:
        logger.error(f"Failed to load {e}")
        return []
    
    # neu du lieu la dict thi chuyen thanh list chua dict. Vi du: { "companyName": "Company A", "description": "..." } => [ { "companyName": "Company A", "description": "..." } ]
    if isinstance(company_info, dict):
        company_info = [company_info]
        
    # kiem tra kieu du lieu co phai la list khong. Vi du: [ { "name": "Company A", "description": "..." }, { "name": "Company B", "description": "..." } ]
    if not isinstance(company_info, list):
        logger.error("Company info data is not a list")
        return []
    
    if not company_info: # kiem tra danh sach co rong khong. Vi du: []
        logger.warning("No company info found in the data")
        return []
    
    chunks = [] # danh sach luu cac doan van ban
    
    for idx, company in enumerate(company_info):
        if not isinstance(company, dict):
            logger.warning(f"Invalid company info at index {idx}: expected a dictionary")
            continue
        
        company_name = company.get("companyName", "") # lay ten cong ty
        if not company_name or not isinstance(company_name, str): # kiem tra ten cong ty co hop le khong. Vi du: "Công ty TNHH XYZ"
            logger.warning(f"Company info at index {idx} due to missing or invalid company name")
            continue
                
        company_description = company.get("companyDescription", "") # lay mo ta cong ty
        if not company_description or not isinstance(company_description, str): # kiem tra mo ta cong ty co hop le khong. Vi du: "Công ty TNHH XYZ chuyên cung cấp các giải pháp xây dựng..."
            logger.warning(f"Company info at index {idx} due to missing or invalid company description")
            continue
        
        company_id = company.get("id") # lay id cong ty
        company_slogan = company.get("companySlogan") # lay slogan cong ty
        company_hotline = company.get("hotlines") # lay hotline cong ty        
        company_email = company.get("emails") # lay email cong ty
        company_address = company.get("mainAddress") # lay dia chi cong ty
        company_working_hours = company.get("workingHours") # lay gio lam viec cong ty
        company_website = company.get("website") # lay website cong ty
        company_total_projects = company.get("totalProjects") # lay tong so du an cong ty da thuc hien
        company_social_links = company.get("socialLinks") # lay cac link mang xa hoi cong ty
        company_social_text = "" # khoi tao bien luu chuoi cac mang xa hoi cua cong ty
        if isinstance(company_social_links, dict): # kiem tra kieu du lieu co phai la dict khong. Vi du: { "facebook": "fb.com/xyz", "instagram": "insta.com/xyz" }
            # chuyen doi dict thanh chuoi. Vi du: "facebook: fb.com/xyz, instagram: insta.com/xyz". Neu gia tri rong thi khong them vao chuoi
            company_social_text = ", ".join([f"{key}: {value}" for key, value in company_social_links.items() if value]) 
        
        text_parts = [
            f'Tên công ty: {company_name}.',
            f'Mô tả công ty: {company_description}.',
        ]
        
        if isinstance(company_slogan, str) and company_slogan: # kiem tra kieu du lieu co phai la str khong. Vi du: "Chất lượng - Uy tín - Tiến độ"
            text_parts.append(f'Slogan công ty: {company_slogan}.')
            
        if isinstance(company_hotline, list) and company_hotline: # kiem tra kieu du lieu co phai la list khong. Vi du: [ "0909123456", "0987654321" ]
            text_parts.append(f'Hotline công ty: {", ".join(company_hotline)}.')
            
        if isinstance(company_email, list) and company_email: # kiem tra kieu du lieu co phai la list khong. Vi du: [ "contact@xyz.com", "support@xyz.com" ]
            text_parts.append(f'Email công ty: {", ".join(company_email)}.')
            
        if isinstance(company_address, str) and company_address: # kiem tra kieu du lieu co phai la str khong. Vi du: "123 Đường ABC, Quận 1, TP.HCM"
            text_parts.append(f'Địa chỉ công ty: {company_address}.')
            
        if isinstance(company_working_hours, str) and company_working_hours: # kiem tra kieu du lieu co phai la str khong. Vi du: "8:00 - 17:00 từ Thứ Hai đến Thứ Sáu"
            text_parts.append(f'Giờ làm việc công ty: {company_working_hours}.')
            
        if isinstance(company_website, str) and company_website: # kiem tra kieu du lieu co phai la str khong. Vi du: "www.xyz.com"
            text_parts.append(f'Website công ty: {company_website}.')
            
        if isinstance(company_total_projects, (int)) and company_total_projects: # kiem tra kieu du lieu co phai la str hoac int khong. Vi du: 150
            text_parts.append(f'Tổng số dự án đã thực hiện: {company_total_projects}.')
            
        if company_social_text:
            text_parts.append(f'Các mạng xã hội của công ty: {company_social_text}.') # them chuoi mang xa hoi neu co
               
        text = "\n".join(text_parts) # noi cac phan thanh chuoi van ban duy nhat
        
        chunks.append ({ 
            "text": text,
            "metadata": {
                "type": "company_info",
                "company_id": company_id,
                "company_name": company_name,
                "source": "companyInfo.json"
            }
        })
        
    if not chunks:
        logger.warning("No valid company info chunks were created")
        
    return chunks