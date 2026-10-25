"""Move sequencing uses actual vacancies and compatible staging; never overwrites."""
from .validation import validate, fit

def move_plan(products,locations,target):
    errors=validate(products,locations,assignment=target)
    if errors: return {'safe':False,'steps':[],'errors':errors}
    ps={p.sku:p for p in products}; ls={l.location_id:l for l in locations}
    current={p.sku:p.location for p in products if p.location}; steps=[]
    pending={s:d for s,d in target.items() if current.get(s)!=d}
    def step(s,d,reason):
        src=current.get(s,'NEW'); previous=len(steps)
        steps.append({'step':previous+1,'sku':s,'source':src,'destination':d,'reason':reason,'dependencies':str(previous) if previous else ''})
        current[s]=d
    while pending:
        occupied=set(current.values())
        ready=next((s for s,d in pending.items() if d not in occupied),None)
        if ready is not None:
            step(ready,pending.pop(ready),'Final placement; route/support objective or new-product placement'); continue
        staged=False
        for s in pending:
            vacancy=next((l for l in locations if l.location_id not in occupied and not l.locked and not fit(ps[s],l)),None)
            if vacancy:
                step(s,vacancy.location_id,'Temporary compatible staging to resolve cycle'); staged=True; break
        if not staged: return {'safe':False,'steps':steps,'errors':['No compatible empty staging location; do not execute partial plan.']}
    return {'safe':True,'steps':steps,'errors':[]}
