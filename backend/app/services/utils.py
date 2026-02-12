"""
Utilidades y helpers para mejorar la mantenibilidad del código.
Centraliza funciones comunes y reduce duplicación.
"""

import os
import re
import uuid
import mimetypes
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from werkzeug.utils import secure_filename
import bleach
import logging

logger = logging.getLogger(__name__)

# Configuraciones centralizadas
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'txt'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/png', 'image/jpeg', 'image/gif',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Configuración de sanitización
ALLOWED_HTML_TAGS = ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li']
ALLOWED_HTML_ATTRIBUTES = {}

class FileUtils:
    """Utilidades para manejo de archivos"""
    
    @staticmethod
    def validate_file(file, max_size: int = MAX_FILE_SIZE) -> Tuple[bool, List[str], Optional[str]]:
        """
        Validar archivo subido de forma exhaustiva
        Returns: (is_valid, errors, secure_filename)
        """
        errors = []
        
        if not file or not file.filename:
            return False, ["No se ha seleccionado ningún archivo"], None
        
        # Sanitizar nombre de archivo
        original_filename = file.filename
        secure_name = secure_filename(original_filename)
        
        if not secure_name:
            errors.append("Nombre de archivo inválido")
            return False, errors, None
        
        # Validar extensión
        if '.' not in secure_name:
            errors.append("El archivo debe tener una extensión")
            return False, errors, None
            
        extension = secure_name.rsplit('.', 1)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            errors.append(f"Extensión no permitida. Permitidas: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # Leer contenido para validaciones
        try:
            file_content = file.read()
            file.seek(0)  # Reset pointer
            
            # Validar tamaño
            if len(file_content) > max_size:
                errors.append(f"Archivo muy grande. Máximo: {max_size / (1024*1024):.1f}MB")
            
            # Validar tipo MIME
            detected_mime, _ = mimetypes.guess_type(secure_name)
            if detected_mime and detected_mime not in ALLOWED_MIME_TYPES:
                errors.append(f"Tipo de archivo no permitido: {detected_mime}")
            
            # Validar contenido malicioso
            if FileUtils._has_malicious_content(file_content):
                errors.append("El archivo contiene contenido potencialmente peligroso")
                
        except Exception as e:
            logger.error(f"Error validating file: {e}")
            errors.append("Error al verificar el archivo")
        
        is_valid = len(errors) == 0
        return is_valid, errors, secure_name if is_valid else None
    
    @staticmethod
    def _has_malicious_content(content: bytes) -> bool:
        """Detectar contenido malicioso en archivos"""
        dangerous_signatures = [
            b'\x4d\x5a',  # MZ header (ejecutables Windows)
            b'\x7f\x45\x4c\x46',  # ELF header (ejecutables Linux)
            b'\xfe\xed\xfa',  # Mach-O header (ejecutables macOS)
            b'<script',  # Scripts
            b'<?php',  # Código PHP
            b'javascript:',  # JavaScript URLs
        ]
        
        file_start = content[:200].lower()
        return any(signature in file_start for signature in dangerous_signatures)
    
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """Generar nombre único para archivo"""
        secure_name = secure_filename(original_filename)
        if not secure_name:
            secure_name = "file"
        
        name, ext = os.path.splitext(secure_name)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        return f"{name}_{timestamp}_{unique_id}{ext}"


class TextUtils:
    """Utilidades para manejo de texto"""
    
    @staticmethod
    def sanitize_html(text: str, allowed_tags: List[str] = None, 
                     allowed_attributes: Dict = None) -> str:
        """Sanitizar HTML de forma segura"""
        if not text:
            return ""
        
        tags = allowed_tags or ALLOWED_HTML_TAGS
        attrs = allowed_attributes or ALLOWED_HTML_ATTRIBUTES
        
        return bleach.clean(text, tags=tags, attributes=attrs, strip=True)
    
    @staticmethod
    def sanitize_string(value: Any, max_length: int = None, 
                       allow_html: bool = False) -> str:
        """Sanitizar string con opciones"""
        if value is None:
            return ""
        
        text = str(value).strip()
        
        if not allow_html:
            # Escapar HTML básico
            text = text.replace('<', '&lt;').replace('>', '&gt;')
        else:
            text = TextUtils.sanitize_html(text)
        
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def generate_slug(text: str, max_length: int = 50) -> str:
        """Generar slug URL-friendly"""
        if not text:
            return ""
        
        # Normalizar texto
        slug = str(text).lower().strip()
        
        # Reemplazar caracteres especiales
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        
        if max_length:
            slug = slug[:max_length]
        
        return slug.strip('-')
    
    @staticmethod
    def truncate_text(text: str, length: int = 100, suffix: str = "...") -> str:
        """Truncar texto con sufijo"""
        if not text or len(text) <= length:
            return text or ""
        
        return text[:length - len(suffix)] + suffix


class DateUtils:
    """Utilidades para manejo de fechas"""
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
        """Formatear fecha de forma consistente"""
        if not dt:
            return ""
        return dt.strftime(format_str)
    
    @staticmethod
    def format_date(dt: datetime, format_str: str = "%d/%m/%Y") -> str:
        """Formatear solo fecha"""
        if not dt:
            return ""
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> Optional[datetime]:
        """Parsear fecha desde string"""
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, format_str)
        except ValueError:
            logger.warning(f"Cannot parse date: {date_str}")
            return None
    
    @staticmethod
    def get_date_range(days: int = 30) -> Tuple[datetime, datetime]:
        """Obtener rango de fechas"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    @staticmethod
    def is_overdue(deadline: datetime, current_time: datetime = None) -> Tuple[bool, int]:
        """Verificar si una fecha está vencida"""
        if not deadline:
            return False, 0
        
        current = current_time or datetime.utcnow()
        
        if current > deadline:
            days_overdue = (current - deadline).days
            return True, days_overdue
        
        return False, 0


class NumberUtils:
    """Utilidades para manejo de números"""
    
    @staticmethod
    def format_currency(value: Union[int, float], currency: str = "$") -> str:
        """Formatear número como moneda"""
        if value is None:
            return f"{currency}0"
        
        try:
            # Convertir a float si es string
            if isinstance(value, str):
                value = float(value)
            
            # Formatear con separadores de miles
            if value % 1 == 0:
                formatted = f"{value:,.0f}"
            else:
                formatted = f"{value:,.2f}"
            
            # Formato colombiano: punto para miles, coma para decimales
            formatted = formatted.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
            
            return f"{currency}{formatted}"
            
        except (ValueError, TypeError):
            logger.warning(f"Cannot format currency: {value}")
            return f"{currency}0"
    
    @staticmethod
    def format_percentage(value: Union[int, float], decimals: int = 2) -> str:
        """Formatear número como porcentaje"""
        if value is None:
            return "0%"
        
        try:
            return f"{float(value):.{decimals}f}%"
        except (ValueError, TypeError):
            return "0%"
    
    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """Convertir a float de forma segura"""
        if value is None:
            return default
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """Convertir a int de forma segura"""
        if value is None:
            return default
        
        try:
            return int(float(value))  # Permite "123.0" -> 123
        except (ValueError, TypeError):
            return default


class ValidationUtils:
    """Utilidades para validación"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validar formato de email"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str, country_code: str = "CO") -> bool:
        """Validar número de teléfono colombiano"""
        if not phone:
            return False
        
        # Limpiar número
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Patrones colombianos
        patterns = [
            r'^\+57\d{10}$',  # +57xxxxxxxxxx
            r'^57\d{10}$',    # 57xxxxxxxxxx
            r'^\d{10}$',      # xxxxxxxxxx
            r'^3\d{9}$',      # 3xxxxxxxxx (celular)
            r'^[1-8]\d{6}$',  # xxxxxxx (fijo)
        ]
        
        return any(re.match(pattern, clean_phone) for pattern in patterns)
    
    @staticmethod
    def validate_nit(nit: str) -> bool:
        """Validar formato de NIT colombiano"""
        if not nit:
            return False
        
        # Limpiar NIT
        clean_nit = re.sub(r'[^\d]', '', nit)
        
        # NIT debe tener entre 8 y 15 dígitos
        return 8 <= len(clean_nit) <= 15
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> Tuple[bool, List[str]]:
        """Validar campos requeridos"""
        missing_fields = []
        
        for field in required_fields:
            value = data.get(field)
            if value is None or str(value).strip() == '':
                missing_fields.append(field)
        
        is_valid = len(missing_fields) == 0
        return is_valid, missing_fields


class SecurityUtils:
    """Utilidades para seguridad"""
    
    @staticmethod
    def detect_suspicious_patterns(text: str) -> List[str]:
        """Detectar patrones sospechosos en texto"""
        if not text:
            return []
        
        text_lower = text.lower()
        suspicious_patterns = []
        
        # Patrones de inyección SQL
        sql_patterns = [
            r'union\s+select', r'drop\s+table', r'delete\s+from',
            r'insert\s+into', r'update\s+set', r'--', r'/\*', r'\*/',
            r'exec\s*\(', r'sp_', r'xp_'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text_lower):
                suspicious_patterns.append(f"SQL_INJECTION:{pattern}")
        
        # Patrones XSS
        xss_patterns = [
            r'<script', r'javascript:', r'onload=', r'onerror=',
            r'eval\s*\(', r'alert\s*\(', r'document\.cookie'
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, text_lower):
                suspicious_patterns.append(f"XSS:{pattern}")
        
        # Patrones de path traversal
        if '../' in text or '..\\' in text:
            suspicious_patterns.append("PATH_TRAVERSAL")
        
        return suspicious_patterns
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generar token seguro"""
        return str(uuid.uuid4()).replace('-', '')[:length]
    
    @staticmethod
    def hash_sensitive_data(data: str) -> str:
        """Hash datos sensibles para logs"""
        if not data:
            return ""
        
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()[:16] + "..."