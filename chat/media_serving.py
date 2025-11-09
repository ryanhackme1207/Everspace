"""
Media file serving utilities for production environments.
Handles serving GIFs and other media files properly in production.
"""

import os
from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound
from django.views.static import serve as serve_static
from django.views.decorators.http import condition
from pathlib import Path


def serve_media_file(request, path):
    """
    Serve media files with proper caching headers.
    This is used when WhiteNoise or Django's static file serving isn't handling media.
    """
    try:
        # Ensure we're serving from MEDIA_ROOT only
        media_root = Path(settings.MEDIA_ROOT)
        file_path = media_root / path
        
        # Security check: ensure file is within MEDIA_ROOT
        try:
            file_path.resolve().relative_to(media_root.resolve())
        except ValueError:
            # Path is outside MEDIA_ROOT
            return HttpResponseNotFound()
        
        # Check if file exists
        if not file_path.exists() or not file_path.is_file():
            return HttpResponseNotFound()
        
        # Serve the file
        return FileResponse(
            open(file_path, 'rb'),
            content_type=get_content_type(file_path)
        )
    except Exception as e:
        print(f"Error serving media file {path}: {str(e)}")
        return HttpResponseNotFound()


def get_content_type(file_path):
    """Determine content type based on file extension"""
    import mimetypes
    content_type, _ = mimetypes.guess_type(str(file_path))
    return content_type or 'application/octet-stream'


class MediaFilesMiddleware:
    """
    Middleware to ensure media files are accessible in production.
    This acts as a fallback when using WhiteNoise or other static servers.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.media_root = Path(settings.MEDIA_ROOT)
        self.media_url = settings.MEDIA_URL.lstrip('/')
    
    def __call__(self, request):
        # Check if this is a media file request
        path = request.path_info
        
        if path.startswith(settings.MEDIA_URL):
            # Extract relative path
            relative_path = path[len(settings.MEDIA_URL):]
            
            # Try to serve the file
            file_path = self.media_root / relative_path
            
            if file_path.exists() and file_path.is_file():
                try:
                    response = FileResponse(
                        open(file_path, 'rb'),
                        content_type=get_content_type(file_path)
                    )
                    # Add cache headers
                    response['Cache-Control'] = 'public, max-age=3600'
                    return response
                except Exception as e:
                    print(f"Error serving media file: {str(e)}")
                    return self.get_response(request)
        
        return self.get_response(request)
