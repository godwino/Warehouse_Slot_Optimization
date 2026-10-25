"""Bounded feasible heuristic; objective and candidate limits are explicit."""
from itertools import combinations
from .models import Config
from .validation import fit, validate
from .evaluation import evidence, proxy, travel
from .movement import move_plan

def optimize(products,locations,orders,config=None,max_passes=3):
    c=config or Config(); baseline={p.sku:p.location for p in products if p.location}
    errors=validate(products,locations,orders,baseline)
    if errors: raise ValueError('; '.join(errors))
    pairs=evidence(products,orders); ls={l.location_id:l for l in locations}
    movable=[p for p in products if p.location and not p.locked and not ls[p.location].locked]
    def score(a):
        return proxy(a,locations,pairs)+c.move_penalty*sum(a[s]!=baseline[s] for s in baseline)+(c.travel_weight*travel(orders,a,locations,c)/max(1,len(orders)) if c.travel_weight else 0)
    best=baseline.copy(); value=score(best); accepted=0
    for _ in range(max_passes):
        winner=None; winner_value=value
        vacancies=[l for l in locations if l.location_id not in best.values() and not l.locked]
        candidates=[]
        for p in movable:
            for l in vacancies:
                if not fit(p,l): candidates.append({p.sku:l.location_id})
        for p,q in combinations(movable,2):
            if not fit(p,ls[best[q.sku]]) and not fit(q,ls[best[p.sku]]): candidates.append({p.sku:best[q.sku],q.sku:best[p.sku]})
        # Bounded three-product cycles over the first twelve movable SKUs.
        for group in combinations(movable[:12],3):
            for order in (group,tuple(reversed(group))):
                change={p.sku:best[order[(i+1)%3].sku] for i,p in enumerate(order)}
                if all(not fit(p,ls[change[p.sku]]) for p in group): candidates.append(change)
        for change in candidates:
            a={**best,**change}; v=score(a)
            if v<winner_value-1e-10 and move_plan(products,locations,a)['safe']:
                winner=a; winner_value=v
        if winner is None: break
        best=winner; value=winner_value; accepted+=1
    return {'assignment':best,'status':'Improvement found' if accepted else 'No improvement found','objective_before':score(baseline),'objective_after':value,
            'optimality_guaranteed':False,'search':'Best feasible vacancy/swap and bounded three-cycle search; at most three passes','plan':move_plan(products,locations,best)}

def place_new(product,products,locations,orders,config=None,max_depth=3,limit=10):
    c=config or Config()
    if product.sku in {p.sku for p in products} or product.location: raise ValueError('New SKU must be unique and unslotted')
    allp=products+[product]; base={p.sku:p.location for p in products if p.location}; ps={p.sku:p for p in allp}; ls={l.location_id:l for l in locations}
    errors=validate(allp,locations,orders,base)
    if errors: raise ValueError('; '.join(errors))
    results=[]
    explored=0
    def paths(s,a,depth,visited):
        nonlocal explored
        p=ps[s]
        for l in locations:
            if explored >= 10000: return
            explored += 1
            if l.locked or l.location_id in visited or fit(p,l): continue
            occupant=next((k for k,v in a.items() if v==l.location_id),None)
            if occupant is None: yield {**a,s:l.location_id}
            elif depth>0 and not ps[occupant].locked and not ls[a[occupant]].locked:
                for relocated in paths(occupant,a,depth-1,visited|{l.location_id}): yield {**relocated,s:l.location_id}
    for a in paths(product.sku,base,max_depth,set()):
        plan=move_plan(allp,locations,a)
        if not plan['safe']: continue
        moved=sum(a[s]!=base[s] for s in base)
        # Cold start uses declared expected line frequency, no invented co-occurrence.
        rank=c.move_penalty*moved+product.expected_frequency*ls[a[product.sku]].route/10000
        results.append({'assignment':a,'location':a[product.sku],'existing_moves':moved,'rank_cost':rank,'plan':plan,
                        'explanation':'Upright dimension, case weight, zone, stock and lock checks passed. Cold-start route preference uses assumed frequency; no historical co-occurrence evidence for this SKU.'})
    results.sort(key=lambda r:(r['rank_cost'],r['existing_moves'],r['location']))
    return {'status':'Options found' if results else 'Infeasible within configured chain depth','options':results[:limit],'max_displacements':max_depth,'candidate_checks':explored,'search_limit':10000}
