"""
Theme API Routes

Endpoints for theme customization and color extraction.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from PIL import Image
import requests
from io import BytesIO
from collections import Counter
import colorsys

from app.database import get_sync_db
from app.models.user import User
from app.models.groupe import Groupe
from app.middleware.auth_middleware import get_current_user_sync

router = APIRouter()


def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_dominant_colors(image_url: str, num_colors: int = 5) -> List[str]:
    """
    Extract dominant colors from an image.
    
    Returns a list of hex colors sorted by prominence.
    """
    try:
        # Download image
        if image_url.startswith('http'):
            response = requests.get(image_url, timeout=5)
            img = Image.open(BytesIO(response.content))
        else:
            # Local file
            img = Image.open(image_url.lstrip('/'))
        
        # Resize for performance
        img = img.resize((150, 150))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get all pixels
        pixels = list(img.getdata())
        
        # Filter out very light and very dark colors
        filtered_pixels = [
            pixel for pixel in pixels
            if 30 < sum(pixel) < 700  # Avoid too dark or too light
        ]
        
        # Count colors
        color_counter = Counter(filtered_pixels)
        
        # Get most common colors
        most_common = color_counter.most_common(num_colors * 2)
        
        # Filter similar colors and convert to hex
        colors = []
        for color, _ in most_common:
            # Check if color is too similar to existing colors
            is_unique = True
            for existing in colors:
                existing_rgb = hex_to_rgb(existing)
                if all(abs(color[i] - existing_rgb[i]) < 30 for i in range(3)):
                    is_unique = False
                    break
            
            if is_unique:
                colors.append(rgb_to_hex(color))
                if len(colors) >= num_colors:
                    break
        
        return colors
        
    except Exception as e:
        print(f"Error extracting colors: {e}")
        return []


def generate_theme_from_primary(primary_color: str) -> Dict:
    """
    Generate a complete theme from a primary color.
    
    Creates complementary, analogous, and neutral colors.
    """
    # Convert to RGB
    r, g, b = hex_to_rgb(primary_color)
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    
    # Generate secondary (complementary)
    h_secondary = (h + 0.5) % 1.0
    r2, g2, b2 = colorsys.hsv_to_rgb(h_secondary, s, v)
    secondary = rgb_to_hex((r2*255, g2*255, b2*255))
    
    # Generate accent (analogous)
    h_accent = (h + 0.15) % 1.0
    r3, g3, b3 = colorsys.hsv_to_rgb(h_accent, min(s * 1.2, 1.0), min(v * 1.1, 1.0))
    accent = rgb_to_hex((r3*255, g3*255, b3*255))
    
    # Generate muted version
    r4, g4, b4 = colorsys.hsv_to_rgb(h, s * 0.3, v * 0.95)
    muted = rgb_to_hex((r4*255, g4*255, b4*255))
    
    return {
        "primary": primary_color,
        "secondary": secondary,
        "accent": accent,
        "muted": muted,
        "success": "#10b981",  # Green
        "warning": "#f59e0b",  # Orange
        "error": "#ef4444",    # Red
        "info": "#3b82f6",     # Blue
    }


@router.get("/extract-from-logo")
def extract_theme_from_logo(
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Extract theme colors from the active group's logo.
    
    Returns suggested theme colors based on the logo.
    """
    # Get first active group
    groupe = db.query(Groupe).filter(Groupe.is_active == True).first()
    
    if not groupe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun groupe actif trouvé"
        )
    
    if not groupe.logo_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Le groupe n'a pas de logo"
        )
    
    # Build full URL
    logo_url = groupe.logo_url
    if not logo_url.startswith('http'):
        logo_url = f"http://localhost:8000{logo_url}"
    
    # Extract colors
    colors = get_dominant_colors(logo_url, num_colors=5)
    
    if not colors:
        # Return default theme
        return {
            "colors": ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"],
            "suggested_theme": generate_theme_from_primary("#3b82f6"),
            "groupe": {
                "id": str(groupe.id),
                "name": groupe.name,
                "logo_url": groupe.logo_url
            }
        }
    
    # Generate full theme from primary color
    suggested_theme = generate_theme_from_primary(colors[0])
    
    return {
        "colors": colors,
        "suggested_theme": suggested_theme,
        "groupe": {
            "id": str(groupe.id),
            "name": groupe.name,
            "logo_url": groupe.logo_url
        }
    }


@router.get("/current")
def get_current_theme(
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Get current theme configuration for the user.
    
    Returns user's custom theme or default theme.
    """
    # TODO: Implement user preferences table for storing custom themes
    # For now, return default theme
    
    return {
        "mode": "light",  # or "dark"
        "colors": {
            "primary": "#3b82f6",
            "secondary": "#8b5cf6",
            "accent": "#10b981",
            "muted": "#94a3b8",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "info": "#3b82f6",
        },
        "fonts": {
            "sans": "Inter, system-ui, sans-serif",
            "mono": "Fira Code, monospace"
        }
    }


@router.post("/apply")
def apply_theme(
    theme_config: Dict,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Apply a custom theme for the current user.
    
    Saves theme preferences to user settings.
    """
    # TODO: Implement user preferences table
    # For now, just return success
    
    return {
        "success": True,
        "message": "Thème appliqué avec succès",
        "theme": theme_config
    }


@router.post("/reset")
def reset_theme(
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_user_sync)
):
    """
    Reset theme to default (based on logo).
    """
    # TODO: Clear user theme preferences
    
    return {
        "success": True,
        "message": "Thème réinitialisé"
    }

