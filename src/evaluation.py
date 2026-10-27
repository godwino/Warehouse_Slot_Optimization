"""Assignment-level sequence proxy and practical pallet-stability scoring."""
from collections import Counter, defaultdict
from itertools import combinations
import hashlib
import json
from dataclasses import asdict
from .models import Config
from .validation import validate


def frequencies(orders):
    freq = Counter(); cases = Counter()
    for o in orders:
        freq[o.sku] += 1
        cases[o.sku] += o.qty
    return {s: {'line_frequency': freq[s], 'case_velocity': cases[s]} for s in freq}


def pair_cost(early, late):
    # Adjacent or nonadjacent pair: earlier cases form potential support for later cases.
    return (
        early.crushability * late.weight_kg / 30
        + (1 - early.support) * late.support
        + max(0, late.weight_kg - early.max_top_kg) / 30
        + max(0, late.length_cm * late.width_cm - early.length_cm * early.width_cm) / 3000
    )


def evidence(products, orders):
    ps = {p.sku: p for p in products}
    pairs = Counter()
    groups = defaultdict(list)
    for o in orders:
        groups[(o.date, o.assignment_id, o.zone)].append(o)
    for lines in groups.values():
        for a, b in combinations(lines, 2):
            if a.sku != b.sku:
                pairs[tuple(sorted((a.sku, b.sku)))] += min(a.qty, b.qty)
    return [
        (a, b, w, pair_cost(ps[a], ps[b]), pair_cost(ps[b], ps[a]))
        for (a, b), w in pairs.items()
    ]


def proxy(a, locations, pairs):
    route = {l.location_id: l.route for l in locations}
    den = sum(x[2] for x in pairs)
    return sum(
        w * (ab if route[a[x]] < route[a[y]] else ba)
        for x, y, w, ab, ba in pairs
    ) / den if den else 0


def sequence(orders, a, locations):
    ls = {l.location_id: l for l in locations}
    return sorted(orders, key=lambda o: ls[a[o.sku]].route)


def travel(orders, a, locations, c):
    ls = {l.location_id: l for l in locations}
    groups = defaultdict(list)
    for o in orders:
        groups[(o.date, o.assignment_id, o.zone)].append(o)
    total = 0
    for lines in groups.values():
        aisles = defaultdict(list)
        for o in lines:
            aisles[ls[a[o.sku]].aisle].append(ls[a[o.sku]].bay)
        order = c.aisle_order.split(',')
        if any(x not in order for x in aisles):
            raise ValueError('Configure aisle order for every active aisle')
        total += sum(2 * (max(bays) - c.start_number + 1) * c.bay_spacing_m for bays in aisles.values())
        total += 2 * max(order.index(x) for x in aisles) * c.aisle_spacing_m
    return total


def stability_score(product_a, product_b, direction='below'):
    """Higher is more stable. Penalize heavy-over-fragile and weak-under-heavy patterns."""
    weight_factor = 1 - min(1.0, abs(product_a.weight_kg - product_b.weight_kg) / 30)
    support = 1.0 if product_a.support >= product_b.support else 0.2
    crush_penalty = product_a.crushability if direction == 'below' else product_b.crushability
    footprint_match = 1.0 - abs(product_a.footprint_m2 - product_b.footprint_m2) / max(0.5, product_b.footprint_m2 + 0.5)
    top_load = 1.0 if product_a.max_top_kg >= product_b.weight_kg else 0.0
    score = (
        weight_factor * 0.30
        + support * 0.25
        + footprint_match * 0.20
        + top_load * 0.25
        - crush_penalty * 0.25
    )
    return max(0.0, min(1.0, score))


def pallet_stability_proxy(products, assignment=None, locations=None):
    """Estimate pallet-building safety from case attributes and route order."""
    current = assignment or {p.sku: p.location for p in products if p.location}
    items = [p for p in products if p.sku in current]
    if not items:
        return {'stability_score': 0.0, 'risk_flags': ['No assignments'], 'heavy_after_fragile': 0}

    route = {l.location_id: l.route for l in locations} if locations else {}
    ordered = sorted(items, key=lambda p: route.get(current[p.sku], current[p.sku]))
    heavy_after_fragile = 0
    risk_flags = []
    for index, item in enumerate(ordered[:-1]):
        next_item = ordered[index + 1]
        if item.crushability > 0.6 and next_item.weight_kg > item.weight_kg * 1.5:
            heavy_after_fragile += 1
            risk_flags.append(f'{item.sku} before heavier case {next_item.sku}')
        if item.weight_kg > next_item.weight_kg and item.crushability > 0.5:
            risk_flags.append(f'Fragile case {item.sku} placed before a lighter case')

    score = 0.0
    for i in range(len(ordered) - 1):
        a = ordered[i]
        b = ordered[i + 1]
        score += stability_score(a, b, direction='below')
    score = score / max(1, len(ordered) - 1)
    return {
        'stability_score': round(score, 4),
        'risk_flags': risk_flags[:10],
        'heavy_after_fragile': heavy_after_fragile,
    }


def evaluate(products, locations, orders, a, config=None):
    c = config or Config()
    errors = validate(products, locations, orders, a)
    if errors:
        raise ValueError('; '.join(errors))
    if c.walking_mps <= 0 or c.handling_seconds < 0:
        raise ValueError('Invalid timing assumptions')
    distance = travel(orders, a, locations, c)
    cases = sum(o.qty for o in orders)
    seconds = distance / c.walking_mps + cases * c.handling_seconds
    stability = pallet_stability_proxy(products, a, locations)
    return {
        'sequence_proxy': proxy(a, locations, evidence(products, orders)),
        'products_moved': sum(a.get(p.sku) != p.location for p in products if p.location),
        'constraint_violations': len(errors),
        'affected_orders': len({(o.date, o.order_id) for o in orders if a[o.sku] != next(p.location for p in products if p.sku == o.sku)}),
        'illustrative_travel_m': distance,
        'modeled_cases_per_hour': cases * 3600 / seconds if seconds else 0,
        'cases': cases,
        'order_lines': len(orders),
        'workload_sha256': hashlib.sha256(json.dumps([asdict(o) for o in orders], sort_keys=True).encode()).hexdigest(),
        'pallet_stability_proxy': stability['stability_score'],
        'heavy_after_fragile_conflicts': stability['heavy_after_fragile'],
        'stability_risk_flags': stability['risk_flags'],
    }


def compare(products, locations, orders, before, after, config=None):
    return {'baseline': evaluate(products, locations, orders, before, config), 'proposed': evaluate(products, locations, orders, after, config)}


def stable_recommendation_table(products, locations, assignment=None):
    """Return practical pallet-building guidance for each product.

    The score combines weight, cube, footprint, support, and crushability to
    estimate whether the current placement is compatible with a safe base-to-top
    pallet build. Higher score means safer current placement for the product.
    """
    ps = {p.sku: p for p in products}
    ls = {l.location_id: l for l in locations}
    current = assignment or {p.sku: p.location for p in products if p.location}
    rows = []
    for product in products:
        if not product.location and product.sku not in current:
            continue
        slot = ls.get(current.get(product.sku, product.location))
        score = 0.0
        reasons = []
        if product.weight_kg >= 18:
            score += 0.25
            reasons.append('Heavy case; suitable for lower pallet layers when support is strong.')
        elif product.weight_kg <= 8:
            score += 0.10
            reasons.append('Light case; generally better in upper pallet layers.')

        if product.support >= 0.75:
            score += 0.25
            reasons.append('Strong support rating; better able to carry or support nearby cases.')
        elif product.support < 0.45:
            score -= 0.15
            reasons.append('Low support rating; avoid placing under heavy or unstable cases.')

        if product.crushability >= 0.75:
            score -= 0.25
            reasons.append('High crushability; keep away from heavy cases and lower load positions.')
        elif product.crushability <= 0.35:
            score += 0.15
            reasons.append('Lower crushability; more suitable for stable lower or middle layers.')

        if product.case_cube_m3 > 0.08:
            score -= 0.10
            reasons.append('Large cube; ensure slot and footprint can support the case without high instability.')
        elif product.case_cube_m3 < 0.03:
            score += 0.08
            reasons.append('Compact footprint; easier to fit into a stable upper or middle layer.')

        if product.height_cm > 40:
            score -= 0.10
            reasons.append('Tall case; avoid using as a base case unless the footprint is very stable.')
        elif product.height_cm < 25:
            score += 0.08
            reasons.append('Shorter case; easier to fit in mid or upper layers.')

        if slot is not None:
            if product.weight_kg > slot.max_supported_weight_kg * 0.8:
                score -= 0.30
                reasons.append('Slot weight approach is near capacity; review if it is a safe lower pallet position.')
            if product.length_cm > slot.usable_length_cm or product.width_cm > slot.usable_width_cm:
                score -= 0.40
                reasons.append('Case exceeds usable slot footprint; physical fit is a constraint.')
            if product.height_cm > slot.usable_height_cm:
                score -= 0.35
                reasons.append('Case exceeds slot height; this is a fit-risk and should be reviewed.')

        if product.max_top_kg < product.weight_kg:
            score -= 0.25
            reasons.append('Product has a low top-load allowance for its weight; avoid high stacking above it.')

        stability_role = 'Base layer'
        if product.weight_kg <= 12 and product.crushability >= 0.6:
            stability_role = 'Top layer'
        elif 12 < product.weight_kg <= 25 and product.crushability < 0.7:
            stability_role = 'Middle layer'

        rows.append({
            'sku': product.sku,
            'product': product.description,
            'category': product.category,
            'weight_kg': round(product.weight_kg, 2),
            'cube_m3': round(product.case_cube_m3, 4),
            'footprint_m2': round(product.footprint_m2, 4),
            'support': round(product.support, 2),
            'crushability': round(product.crushability, 2),
            'current_slot': current.get(product.sku, product.location),
            'stability_role': stability_role,
            'stability_score': round(max(0.0, min(1.0, score)), 3),
            'reason': ' ; '.join(dict.fromkeys(reasons)) if reasons else 'No material stability concern in the demo assumptions.',
        })

    return sorted(rows, key=lambda row: (-row['stability_score'], row['weight_kg']))
