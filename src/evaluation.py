"""Assignment-level sequence proxy and front-entry/front-exit illustrative travel."""
from collections import Counter, defaultdict
from itertools import combinations
import hashlib
import json
from dataclasses import asdict
from .models import Config
from .validation import validate

def frequencies(orders):
    freq=Counter(); cases=Counter()
    for o in orders: freq[o.sku]+=1; cases[o.sku]+=o.qty
    return {s:{'line_frequency':freq[s],'case_velocity':cases[s]} for s in freq}

def pair_cost(early, late):
    # Adjacent or nonadjacent pair: earlier cases form potential support for later cases.
    return (early.crushability * late.weight_kg/30 + (1-early.support)*late.support
            + max(0,late.weight_kg-early.max_top_kg)/30
            + max(0,late.length_cm*late.width_cm-early.length_cm*early.width_cm)/3000)

def evidence(products,orders):
    ps={p.sku:p for p in products}; pairs=Counter()
    groups=defaultdict(list)
    for o in orders: groups[(o.date,o.assignment_id,o.zone)].append(o)
    for lines in groups.values():
        for a,b in combinations(lines,2):
            if a.sku!=b.sku: pairs[tuple(sorted((a.sku,b.sku)))]+=min(a.qty,b.qty)
    return [(a,b,w,pair_cost(ps[a],ps[b]),pair_cost(ps[b],ps[a])) for (a,b),w in pairs.items()]

def proxy(a,locations,pairs):
    route={l.location_id:l.route for l in locations}; den=sum(x[2] for x in pairs)
    return sum(w*(ab if route[a[x]]<route[a[y]] else ba) for x,y,w,ab,ba in pairs)/den if den else 0.

def sequence(orders,a,locations):
    ls={l.location_id:l for l in locations}
    return sorted(orders,key=lambda o:ls[a[o.sku]].route)

def travel(orders,a,locations,c):
    ls={l.location_id:l for l in locations}; groups=defaultdict(list)
    for o in orders: groups[(o.date,o.assignment_id,o.zone)].append(o)
    total=0
    for lines in groups.values():
        aisles=defaultdict(list)
        for o in lines: aisles[ls[a[o.sku]].aisle].append(ls[a[o.sku]].bay)
        order=c.aisle_order.split(',')
        if any(x not in order for x in aisles): raise ValueError('Configure aisle order for every active aisle')
        # Start/end at front of first aisle. Return to front after each aisle; ascending picks.
        total+=sum(2*(max(bays)-c.start_number+1)*c.bay_spacing_m for bays in aisles.values())
        total+=2*max(order.index(x) for x in aisles)*c.aisle_spacing_m
    return total

def evaluate(products,locations,orders,a,config=None):
    c=config or Config(); errors=validate(products,locations,orders,a)
    if errors: raise ValueError('; '.join(errors))
    if c.walking_mps<=0 or c.handling_seconds<0: raise ValueError('Invalid timing assumptions')
    distance=travel(orders,a,locations,c); cases=sum(o.qty for o in orders)
    seconds=distance/c.walking_mps+cases*c.handling_seconds
    return {'sequence_proxy':proxy(a,locations,evidence(products,orders)), 'products_moved':sum(a.get(p.sku)!=p.location for p in products if p.location),
            'constraint_violations':len(errors),'affected_orders':len({(o.date,o.order_id) for o in orders if a[o.sku]!=next(p.location for p in products if p.sku==o.sku)}),
            'illustrative_travel_m':distance,'modeled_cases_per_hour':cases*3600/seconds if seconds else 0,
            'cases':cases,'order_lines':len(orders),'workload_sha256':hashlib.sha256(json.dumps([asdict(o) for o in orders],sort_keys=True).encode()).hexdigest()}

def compare(products,locations,orders,before,after,config=None):
    return {'baseline':evaluate(products,locations,orders,before,config),'proposed':evaluate(products,locations,orders,after,config)}
