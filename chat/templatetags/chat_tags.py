"""
Custom template tags for chat messages
"""
import re
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def render_message_content(content):
    """
    Process message content to render GIF tags as img elements
    Converts [GIF]url[/GIF] to <img src="url" alt="GIF" class="message-gif">
    """
    if not content:
        return ''
    
    # Escape HTML first to prevent XSS
    safe_content = escape(content)
    
    # Replace [GIF]url[/GIF] with proper img tags
    gif_pattern = r'\[GIF\](https?://[^\]]+)\[/GIF\]'
    
    def replace_gif(match):
        gif_url = match.group(1)
        return f'<img src="{gif_url}" alt="GIF" class="message-gif" loading="lazy" onerror="this.style.display=\'none\'">'
    
    result = re.sub(gif_pattern, replace_gif, safe_content)
    
    return mark_safe(result)
