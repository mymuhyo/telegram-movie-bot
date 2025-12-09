"""Quality value object."""

from enum import Enum


class Quality(str, Enum):
    """Movie quality enumeration."""

    SD = "SD"
    HD = "HD"
    FULL_HD = "FullHD"
    UHD_4K = "4K"

    @property
    def display_name(self) -> str:
        """Get display name for quality."""
        names = {
            Quality.SD: "SD (480p)",
            Quality.HD: "HD (720p)",
            Quality.FULL_HD: "Full HD (1080p)",
            Quality.UHD_4K: "4K UHD",
        }
        return names.get(self, self.value)

    @property
    def emoji(self) -> str:
        """Get emoji for quality."""
        emojis = {
            Quality.SD: "📺",
            Quality.HD: "📺",
            Quality.FULL_HD: "🎬",
            Quality.UHD_4K: "🎥",
        }
        return emojis.get(self, "📺")

    @classmethod
    def from_string(cls, value: str) -> "Quality":
        """Create Quality from string."""
        value_upper = value.upper().replace(" ", "").replace("_", "")
        mapping = {
            "SD": cls.SD,
            "480P": cls.SD,
            "HD": cls.HD,
            "720P": cls.HD,
            "FULLHD": cls.FULL_HD,
            "1080P": cls.FULL_HD,
            "FHD": cls.FULL_HD,
            "4K": cls.UHD_4K,
            "UHD": cls.UHD_4K,
            "2160P": cls.UHD_4K,
        }
        if value_upper in mapping:
            return mapping[value_upper]
        return cls.HD  # Default
