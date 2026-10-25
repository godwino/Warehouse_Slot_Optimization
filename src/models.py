"""Typed grocery masters. All dimensions are case-level, upright orientation."""
from dataclasses import dataclass, asdict

@dataclass
class Product:
    sku: str
    description: str
    category: str
    zone: str
    weight_kg: float
    length_cm: float
    width_cm: float
    height_cm: float
    packaging: str = 'carton'
    support: float = 0.5
    crushability: float = 0.5
    max_top_kg: float = 15
    location: str = ''
    locked: bool = False
    expected_frequency: float = 0
    required_stock: int = 1
    allowed_levels: str = '1'

    @property
    def volume_cm3(self):
        return self.length_cm * self.width_cm * self.height_cm

@dataclass
class Location:
    location_id: str
    zone: str
    aisle: str
    bay: int
    level: int
    route: int
    length_cm: float = 65
    width_cm: float = 55
    height_cm: float = 50
    case_weight_limit_kg: float = 30
    locked: bool = False
    stock_capacity: int = 20
    rack_load_limit_kg: float = 600
    replenishment_allowed: bool = True

@dataclass
class OrderLine:
    date: str
    order_id: str
    assignment_id: str
    sku: str
    qty: int
    zone: str

@dataclass
class Config:
    aisle_order: str = 'D3,D4,D5'
    start_number: int = 1
    end_number: int = 48
    bay_spacing_m: float = 1.2
    aisle_spacing_m: float = 3.2
    walking_mps: float = 1.2
    handling_seconds: float = 5.0
    move_penalty: float = 0.002
    travel_weight: float = 0.0
