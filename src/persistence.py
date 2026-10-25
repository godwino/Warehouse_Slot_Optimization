"""Local SQLite snapshots and append-only review events; no operational execution."""
import json
import sqlite3
import math
from datetime import datetime, timezone
from dataclasses import asdict
from .models import Product,Location,OrderLine,Config
from .validation import validate
from .movement import move_plan

def snapshot(products,locations,orders,config,assignment):
    return {'version':1,'products':[asdict(p) for p in products],'locations':[asdict(l) for l in locations],'orders':[asdict(o) for o in orders],'config':asdict(config),'assignment':assignment}

def restore(data):
    if data['version']!=1: raise ValueError('Unsupported scenario version')
    p=[Product(**r) for r in data['products']]; l=[Location(**r) for r in data['locations']]; o=[OrderLine(**r) for r in data['orders']]; c=Config(**data['config']); a=data['assignment']
    errors=validate(p,l,o)+validate(p,l,o,a)
    if errors: raise ValueError('; '.join(errors))
    if any(not math.isfinite(v) for v in [c.bay_spacing_m,c.aisle_spacing_m,c.walking_mps,c.handling_seconds,c.move_penalty,c.travel_weight]): raise ValueError('Configuration numbers must be finite')
    if len(c.aisle_order.split(',')) != len(set(c.aisle_order.split(','))): raise ValueError('Duplicate aisle in route')
    if any(not c.start_number <= x.bay <= c.end_number for x in l): raise ValueError('Bay outside configured bounds')
    if not c.aisle_order or c.end_number<c.start_number or c.bay_spacing_m<=0 or c.aisle_spacing_m<=0 or c.walking_mps<=0 or c.handling_seconds<0 or c.move_penalty<0 or c.travel_weight<0: raise ValueError('Invalid configuration')
    if any(x.aisle not in c.aisle_order.split(',') for x in l): raise ValueError('Missing aisle in route configuration')
    return p,l,o,c,a

class Store:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.executescript('CREATE TABLE IF NOT EXISTS scenarios(id INTEGER PRIMARY KEY,name TEXT,payload TEXT,created TEXT); CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY,scenario INTEGER,status TEXT,reviewer TEXT,notes TEXT,created TEXT);')
    def save(self,name,payload):
        restore(payload)
        with self.db:
            cur=self.db.execute('INSERT INTO scenarios(name,payload,created) VALUES(?,?,?)',(name,json.dumps(payload),datetime.now(timezone.utc).isoformat()))
            sid=cur.lastrowid
            self.db.execute('INSERT INTO reviews(scenario,status,reviewer,notes,created) VALUES(?,?,?,?,?)',(sid,'draft','','',datetime.now(timezone.utc).isoformat()))
        return sid
    def list(self): return self.db.execute('SELECT id,name,created FROM scenarios ORDER BY id DESC').fetchall()
    def load(self,sid):
        row=self.db.execute('SELECT payload FROM scenarios WHERE id=?',(sid,)).fetchone()
        if row is None: raise ValueError('Unknown scenario')
        return json.loads(row[0])
    def history(self,sid): return self.db.execute('SELECT status,reviewer,notes,created FROM reviews WHERE scenario=? ORDER BY id',(sid,)).fetchall()
    def review(self,sid,status,reviewer,notes):
        p,l,o,c,a=restore(self.load(sid)); previous=self.history(sid)[-1][0]
        allowed={'draft':{'reviewed','rejected'},'reviewed':{'approved','rejected'},'approved':set(),'rejected':set()}
        if status not in allowed[previous]: raise ValueError(f'Cannot transition {previous} to {status}')
        if not reviewer.strip() or not notes.strip(): raise ValueError('Reviewer name and notes required')
        if status=='approved' and not move_plan(p,l,a)['safe']: raise ValueError('Safe movement plan required')
        with self.db: self.db.execute('INSERT INTO reviews(scenario,status,reviewer,notes,created) VALUES(?,?,?,?,?)',(sid,status,reviewer,notes,datetime.now(timezone.utc).isoformat()))
