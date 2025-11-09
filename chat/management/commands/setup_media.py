"""
Management command to initialize media directories and ensure they're accessible.
This command should be run during deployment to ensure GIFs and other media files
are properly set up.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Setup media directories and ensure they exist'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        
        # Get media root
        media_root = settings.MEDIA_ROOT
        
        if isinstance(media_root, str):
            media_root = Path(media_root)
        
        # Create subdirectories
        subdirs = [
            'gifs',
            'gifs/thumbnails',
            'profile_pictures',
            'cover_images',
        ]
        
        self.stdout.write(
            self.style.SUCCESS(f'Setting up media directories at: {media_root}')
        )
        
        try:
            # Create main media directory
            media_root.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            for subdir in subdirs:
                dir_path = media_root / subdir
                dir_path.mkdir(parents=True, exist_ok=True)
                if verbose:
                    self.stdout.write(f'  ✓ Created: {dir_path}')
            
            # Check permissions
            if os.access(media_root, os.W_OK | os.R_OK):
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Media directory is readable and writable')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Media directory may have permission issues')
                )
            
            # Log directory info
            if verbose:
                self.stdout.write(self.style.SUCCESS('\nMedia Directory Information:'))
                self.stdout.write(f'  Root: {media_root}')
                self.stdout.write(f'  Exists: {media_root.exists()}')
                self.stdout.write(f'  Is Directory: {media_root.is_dir()}')
                self.stdout.write(f'  Readable: {os.access(media_root, os.R_OK)}')
                self.stdout.write(f'  Writable: {os.access(media_root, os.W_OK)}')
            
            self.stdout.write(
                self.style.SUCCESS('✓ Media setup completed successfully')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error setting up media directories: {str(e)}')
            )
            raise
