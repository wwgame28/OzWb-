from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Product:
    marketplace: str
    category: str
    product_id: str
    title: str
    current_price: float
    url: str
    image_url: str | None = None
    brand: str | None = None
    rating: float | None = None
    review_count: int | None = None
    seller: str | None = None
    available: bool = True
    collected_at: datetime | None = None
