"""Hard constraints and atomic CSV validation; errors retain row context."""
import csv
import io
import math
from dataclasses import fields, asdict
from .models import Product, Location, OrderLine

SCHEMAS = {'products': Product, 'locations': Location, 'orders': OrderLine}

def fit(p, l):
    errors = []
    if p.zone != l.zone: errors.append('approved zone mismatch')
    if not ((p.length_cm <= l.length_cm and p.width_cm <= l.width_cm) or
            (p.width_cm <= l.length_cm and p.length_cm <= l.width_cm)) or p.height_cm > l.height_cm:
        errors.append('upright case dimensions exceed slot (base rotation allowed)')
    if p.weight_kg > l.case_weight_limit_kg: errors.append('case weight exceeds limit')
    if str(l.level) not in p.allowed_levels.split('|'): errors.append('level restriction')
    if p.required_stock > l.stock_capacity: errors.append('pick-face stock capacity insufficient')
    if p.required_stock * p.weight_kg > l.rack_load_limit_kg: errors.append('declared stock exceeds rack load limit')
    if p.required_stock > 1 and not l.replenishment_allowed: errors.append('replenishment prohibited')
    return errors

def validate(products, locations, orders=(), assignment=None):
    errors = []
    for rows, key, name in [(products,'sku','product'),(locations,'location_id','location')]:
        ids = [getattr(x,key) for x in rows]
        if len(ids) != len(set(ids)): errors.append(f'duplicate {name} IDs')
    ps = {p.sku:p for p in products}; ls = {l.location_id:l for l in locations}
    if len({(l.zone,l.route) for l in locations}) != len(locations): errors.append('duplicate route sequence within zone')
    for p in products:
        if not isinstance(p.required_stock,int) or not isinstance(p.locked,bool): errors.append(f'{p.sku}: stock must be integer and locked boolean')
        if not all([p.sku,p.description,p.category,p.zone,p.packaging,p.allowed_levels]): errors.append(f'{p.sku}: missing required text')
        if any(not math.isfinite(v) or v <= 0 for v in [p.weight_kg,p.length_cm,p.width_cm,p.height_cm,p.required_stock]): errors.append(f'{p.sku}: positive finite dimensions, weight and stock required')
        if not 0 <= p.support <= 1 or not 0 <= p.crushability <= 1 or not math.isfinite(p.max_top_kg) or p.max_top_kg < 0 or not math.isfinite(p.expected_frequency) or p.expected_frequency < 0: errors.append(f'{p.sku}: invalid support/crushability/top-load/frequency')
    for l in locations:
        if any(not isinstance(v,int) for v in [l.bay,l.level,l.route,l.stock_capacity]): errors.append(f'{l.location_id}: bay, level, route and capacity must be integers')
        if not all([l.location_id,l.zone,l.aisle]): errors.append(f'{l.location_id}: missing required text')
        if any(not math.isfinite(v) or v <= 0 for v in [l.length_cm,l.width_cm,l.height_cm,l.case_weight_limit_kg,l.stock_capacity,l.rack_load_limit_kg,l.level]) or l.route < 0: errors.append(f'{l.location_id}: invalid capacity/dimensions/route')
    a = assignment if assignment is not None else {p.sku:p.location for p in products if p.location}
    occupied = {}
    for sku, dest in a.items():
        if sku not in ps or dest not in ls:
            errors.append(f'{sku}: unknown SKU/location {dest}'); continue
        p,l = ps[sku],ls[dest]
        if dest in occupied: errors.append(f'{dest}: duplicate occupancy')
        occupied[dest] = sku
        errors.extend(f'{sku} -> {dest}: {e}' for e in fit(p,l))
        if p.location != dest and (p.locked or l.locked or (p.location in ls and ls[p.location].locked)): errors.append(f'{sku}: locked product/source/destination')
    for zone in {l.zone for l in locations}:
        route=sorted([l for l in locations if l.zone==zone],key=lambda l:l.route)
        visited=[]; previous=None
        for loc in route:
            if previous and previous.aisle==loc.aisle and previous.bay>loc.bay: errors.append(f'{zone}: route must pick ascending bay numbers in {loc.aisle}')
            if previous is None or previous.aisle!=loc.aisle:
                if loc.aisle in visited: errors.append(f'{zone}: route revisits aisle {loc.aisle}')
                visited.append(loc.aisle)
            previous=loc
    for p in products:
        if p.location and p.sku not in a: errors.append(f'{p.sku}: existing product omitted')
    groups = {}
    seen = set()
    from datetime import date
    for i,o in enumerate(orders,2):
        try: date.fromisoformat(o.date)
        except ValueError: errors.append(f'orders row {i}: invalid ISO date')
        if not o.order_id or not o.assignment_id: errors.append(f'orders row {i}: order and assignment required')
        if o.sku not in ps: errors.append(f'orders row {i}: unknown SKU {o.sku}')
        elif o.zone != ps[o.sku].zone or o.sku not in a: errors.append(f'orders row {i}: zone mismatch or unslotted SKU')
        if not isinstance(o.qty,int) or o.qty <= 0: errors.append(f'orders row {i}: positive integer quantity required')
        key=(o.date,o.order_id,o.assignment_id,o.sku)
        if key in seen: errors.append(f'orders row {i}: duplicate order line')
        seen.add(key)
        group=(o.date,o.assignment_id)
        if group in groups and groups[group] != (o.zone,o.order_id): errors.append(f'orders row {i}: assignment spans zones/orders')
        groups[group]=(o.zone,o.order_id)
    if len(products) > len(locations): errors.append('insufficient total slot capacity')
    return errors

def csv_text(kind, rows=()):
    out=io.StringIO(); w=csv.DictWriter(out,fieldnames=[f.name for f in fields(SCHEMAS[kind])]); w.writeheader()
    w.writerows(asdict(x) for x in rows); return out.getvalue()

def read_csv(kind, text):
    cls=SCHEMAS[kind]; rows=[]; errors=[]
    reader=csv.DictReader(io.StringIO(text.lstrip('\ufeff')))
    names={f.name for f in fields(cls)}
    if set(reader.fieldnames or []) != names: return [], [f'{kind}: columns must exactly match template: {sorted(names)}']
    for n,row in enumerate(reader,2):
        try:
            values={}
            for f in fields(cls):
                v=row[f.name]
                if v is None: raise ValueError(f'missing {f.name}')
                v=v.strip()
                if f.type is bool:
                    if v.lower() not in ('true','false'): raise ValueError(f'{f.name} must be true/false')
                    values[f.name]=v.lower()=='true'
                else: values[f.name]=f.type(v)
            rows.append(cls(**values))
        except (ValueError,TypeError,KeyError) as e: errors.append(f'{kind} row {n}: {e}')
    return ([],errors) if errors else (rows,[])
