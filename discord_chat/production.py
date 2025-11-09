import os
from decouple import config
from .settings import *

# Production settings
DEBUG = config('DEBUG', default=False, cast=bool)

# Configure ALLOWED_HOSTS for production
ALLOWED_HOSTS = [
    '.onrender.com',
    'everspace-izi3.onrender.com',
    'localhost',
    '127.0.0.1',
]

# Add any additional hosts from environment variable
env_hosts = config('ALLOWED_HOSTS', default='')
if env_hosts:
    ALLOWED_HOSTS.extend([host.strip() for host in env_hosts.split(',') if host.strip()])

# Database configuration for production
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Fallback to SQLite if no DATABASE_URL is provided
    print("WARNING: No DATABASE_URL found. Using SQLite as fallback.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Security settings
SECRET_KEY = config('SECRET_KEY', default=SECRET_KEY)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration - critical for GIFs and Gifts
MEDIA_URL = '/media/'
# Use Render's persistent disk mount point if available, otherwise use local media folder
RENDER_DISK_MOUNT = os.environ.get('RENDER_DISK_MOUNT_PATH')
if RENDER_DISK_MOUNT:
    MEDIA_ROOT = os.path.join(RENDER_DISK_MOUNT, 'media')
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ensure media root exists
try:
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    # Create subdirectories
    for subdir in ['gifs', 'gifs/thumbnails', 'profile_pictures', 'cover_images']:
        os.makedirs(os.path.join(MEDIA_ROOT, subdir), exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create media directories: {e}")

# WhiteNoise middleware is already configured in base settings.py

# Redis configuration for production
REDIS_URL = config('REDIS_URL', default=None)

if REDIS_URL:
    # Redis is available - use for caching and channels
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 20,
                    'socket_connect_timeout': 5,
                    'socket_timeout': 5,
                }
            }
        }
    }

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [REDIS_URL],
                'capacity': 1500,
                'expiry': 60,
            },
        },
    }
else:
    # Fallback to in-memory backends when Redis is not available
    print("WARNING: Redis not configured. Using fallback backends.")
    
    # Use locmem cache as it's more reliable than database cache in production
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'everspace-cache',
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
            }
        }
    }
    
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer'
        }
    }

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}