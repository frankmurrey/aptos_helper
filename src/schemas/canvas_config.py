from pydantic import BaseModel


class CanvasConfig(BaseModel):
    default_color: int
    draw_enabled_for_non_admin: bool
    height: int
    max_number_of_pixels_per_draw: int
    per_account_timeout_s: int
    width: int
