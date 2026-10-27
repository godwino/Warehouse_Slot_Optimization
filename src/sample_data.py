"""Deterministic synthetic Zone 1 pilot; values are illustrative, not specifications."""
import random
from .models import Product, Location, OrderLine, Config

def sample(config=None, seed=42):
    c=config or Config(); rng=random.Random(seed)
    if len(c.aisle_order.split(',')) != len(set(c.aisle_order.split(','))): raise ValueError('Aisle names must be unique')
    locations=[Location(f'{a}-{b:02d}', 'Zone 1', a,b,1,i*(c.end_number-c.start_number+1)+b-c.start_number)
               for i,a in enumerate(c.aisle_order.split(',')) for b in range(c.start_number,c.end_number+1)]
    if len(locations)<63: raise ValueError('Demo requires at least 63 slots')
    families=[('Vinegar',12,0.9,0.15,'rigid jug'),('Water',15,0.85,0.2,'shrink wrap'),('Pepsi',11,0.75,0.25,'tray'),('Juice',12,0.7,0.3,'carton'),('Great Value cola',14,0.8,0.2,'tray'),('Rice',18,0.9,0.1,'bag'),('Chips',2,0.1,0.95,'fragile carton')]
    variants=['Original','Family Pack','Classic','Large Pack','Value Pack','Premium','Regular','Bulk','Select']
    products=[]
    indices=list(range(63)); rng.shuffle(indices)
    for i in range(63):
        name,w,s,cr,pack=families[i%7]
        length,width,height={
            'Vinegar':(40,30,32),'Water':(42,28,26),'Pepsi':(40,27,18),
            'Juice':(38,26,30),'Great Value cola':(41,28,19),
            'Rice':(50,32,16),'Chips':(55,38,42)}[name]
        factor=1+(i//7-4)*0.025
        products.append(Product(f'G{i+1:03d}',f'{name} {variants[i//7]}',name,'Zone 1',round(w*factor,2),length,width,height,pack,s,cr,3 if cr>.8 else 35,locations[indices[i]].location_id,i<2,0,4))
    locations[-1].locked=True
    orders=[]
    for day in range(30):
        for j in range(8):
            aid=f'A{day:02d}-{j:02d}'
            chosen=rng.sample(products,10)
            for p in chosen: orders.append(OrderLine(f'2026-09-{day+1:02d}',f'O{day:02d}-{j//2:02d}',aid,p.sku,rng.randint(1,4),'Zone 1'))
    for p in products:
        lines=[o for o in orders if o.sku==p.sku]
        p.expected_frequency=len(lines)
        p.pick_visits_per_day=round(len(lines)/30,2)
        p.avg_cases_per_day=round(sum(o.qty for o in lines)/30,2)
    return products,locations,orders
