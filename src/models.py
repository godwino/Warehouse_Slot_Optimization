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
    crushability_category: str = 'medium'
    stackability: float = 0.5
    allowed_orientations: str = 'front'
    avg_cases_per_day: float = 0.0
    pick_visits_per_day: float = 0.0
    replenishment_lead_time_days: int = 1
    handling_restrictions: str = ''
    current_location: str = ''

    @property
    def volume_cm3(self):
        return self.length_cm * self.width_cm * self.height_cm

    @property
    def case_cube_m3(self):
        return (self.length_cm * self.width_cm * self.height_cm) / 1_000_000

    @property
    def footprint_m2(self):
        return (self.length_cm * self.width_cm) / 10_000

    @property
    def stability_index(self):
        return (self.support * 0.5) + ((1 - self.crushability) * 0.5)

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
    usable_length_cm: float = 65
    usable_width_cm: float = 55
    usable_height_cm: float = 50
    max_supported_weight_kg: float = 30
    usable_capacity: int = 20
    current_sku: str = ''
    location_restrictions: str = ''

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
