# INSTRUCCIONES PARA CONFIGURACIÓN DE ENTORNO

## Variables de Entorno Requeridas

Crear un archivo `.env` en la carpeta `backend/` con las siguientes variables:

```env
SECRET_KEY=tu_clave_secreta_muy_larga_y_aleatoria_aqui
DATABASE_URL=sqlite:///site.db
```

## Generar SECRET_KEY Segura

Para generar una clave secreta criptográficamente segura, ejecuta este comando de Python:

```python
import secrets
print(secrets.token_hex(32))
```

O alternativamente:

```python
import os
print(os.urandom(24).hex())
```

## Configuración de Producción

Para producción, asegúrate de:
1. Usar una base de datos PostgreSQL o MySQL en lugar de SQLite
2. Configurar HTTPS
3. Usar variables de entorno del sistema en lugar de archivos .env

## Ejemplo de .env

```env
SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
DATABASE_URL=sqlite:///site.db
FLASK_ENV=production
UPLOAD_FOLDER=frontend/static/uploads
MAX_CONTENT_LENGTH=16777216
```