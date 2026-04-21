"""
Configuración global de la aplicación
"""
# Contraseña del administrador (en V2 será configurable desde interfaz)
ADMIN_PASSWORD = "admin123"

# Tamaño máximo de archivos (5MB = 5 * 1024 * 1024 bytes)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Extensiones permitidas para archivos
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt',
                       '.zip', '.xlsx', '.xls', '.ppt', '.pptx'}

# Configuración de la aplicación
APP_NAME = "Sistema de Gestión Escolar"
APP_VERSION = "1.0"