import unittest, tempfile
from dataclasses import replace
from pathlib import Path
from src.models import Product,Location,OrderLine,Config
from src.validation import fit,validate,read_csv,csv_text
from src.movement import move_plan
from src.optimization import optimize,place_new
from src.evaluation import frequencies,compare,travel
from src.sample_data import sample
from src.persistence import Store,snapshot,restore

class GroceryTests(unittest.TestCase):
 def setUp(self):
  self.l=[Location(f'L{i}','Z','D3',i+1,1,i) for i in range(4)]
  self.p=[Product('soft','Chips','chips','Z',2,40,30,20,support=.1,crushability=1,max_top_kg=1,location='L0'),Product('strong','Water','water','Z',20,40,30,20,support=1,crushability=0,max_top_kg=40,location='L1')]
  self.o=[OrderLine('2026-09-01','O','A',p.sku,2,'Z') for p in self.p]; self.a={p.sku:p.location for p in self.p}
 def test_constraints(self):
  p=self.p[0]
  for changed in [replace(p,length_cm=200),replace(p,weight_kg=100),replace(p,zone='bad'),replace(p,required_stock=21),replace(p,allowed_levels='2')]: self.assertTrue(fit(changed,self.l[0]))
  self.assertFalse(fit(replace(p,length_cm=50,width_cm=60),self.l[0]))
  self.assertTrue(validate(self.p,self.l,assignment={'soft':'L0','strong':'L0'}))
  for field in ['product','location']:
   if field=='product': self.p[0].locked=True
   else: self.p[0].locked=False; self.l[0].locked=True
   self.assertTrue(validate(self.p,self.l,assignment={'soft':'L2','strong':'L1'}))
 def test_new_and_displacement(self):
  new=replace(self.p[0],sku='new',location='')
  self.assertEqual(place_new(new,self.p,self.l,self.o,max_depth=0)['options'][0]['existing_moves'],0)
  for l in self.l[1:]:l.length_cm=20
  for p in self.p:p.length_cm=15; p.width_cm=15
  r=place_new(new,self.p,self.l,self.o,max_depth=2)
  self.assertTrue(r['options']); self.assertGreater(r['options'][0]['existing_moves'],0)
  self.assertTrue(move_plan(self.p,self.l,{'soft':'L1','strong':'L2'})['safe'])
 def test_infeasible(self):
  self.assertFalse(place_new(replace(self.p[0],sku='new',location='',length_cm=500),self.p,self.l,self.o)['options'])
  self.assertTrue(validate(self.p,self.l[:1]))
 def test_cycle(self):
  target={'soft':'L1','strong':'L0'}; plan=move_plan(self.p,self.l,target)
  self.assertTrue(plan['safe']); self.assertEqual(len(plan['steps']),3)
  occupancy={p.location:p.sku for p in self.p}
  for s in plan['steps']:
   self.assertNotIn(s['destination'],occupancy); self.assertEqual(occupancy.pop(s['source']),s['sku']); occupancy[s['destination']]=s['sku']
  self.assertFalse(move_plan(self.p,self.l[:2],target)['safe'])
 def test_metrics_and_search(self):
  r=optimize(self.p,self.l,self.o); self.assertEqual(r['status'],'Improvement found')
  result=compare(self.p,self.l,self.o,self.a,r['assignment'])
  self.assertEqual(result['baseline']['workload_sha256'],result['proposed']['workload_sha256'])
  self.assertLess(result['proposed']['sequence_proxy'],result['baseline']['sequence_proxy'])
  self.assertEqual(frequencies(self.o)['soft'],{'line_frequency':1,'case_velocity':2})
  self.assertAlmostEqual(travel(self.o,self.a,self.l,Config()),4.8)
  self.assertAlmostEqual(result['baseline']['sequence_proxy'],2.2)
  for p in self.p:p.locked=True
  self.assertEqual(optimize(self.p,self.l,self.o)['status'],'No improvement found')
 def test_csv(self):
  rows,err=read_csv('products',csv_text('products',self.p)); self.assertFalse(err); self.assertEqual(rows,self.p)
  self.assertTrue(read_csv('products','sku\nx\n')[1]); self.assertTrue(read_csv('products',csv_text('products',self.p).replace('False','maybe'))[1])
  self.assertTrue(validate(self.p+[self.p[0]],self.l,self.o)); self.assertTrue(validate(self.p,self.l,[replace(self.o[0],sku='unknown')]))
 def test_store(self):
  with tempfile.TemporaryDirectory() as d:
   store=Store(Path(d)/'db'); payload=snapshot(self.p,self.l,self.o,Config(),self.a); sid=store.save('test',payload)
   self.assertEqual(store.load(sid),payload); restore(payload)
   with self.assertRaises(ValueError):store.review(sid,'approved','QA','ok')
   store.review(sid,'reviewed','QA','checked'); store.review(sid,'approved','QA','pilot approved')
   store.db.close()
   reopened=Store(Path(d)/'db'); self.assertEqual(reopened.history(sid)[-1][0],'approved'); reopened.db.close()
 def test_sample(self):
  p,l,o=sample(); self.assertEqual(sample(),(p,l,o)); self.assertGreaterEqual(len(p),60); self.assertEqual(len({x.date for x in o}),30); self.assertFalse(validate(p,l,o))
  p,l,o=sample(Config(start_number=11,end_number=58)); self.assertEqual(l[0].bay,11); self.assertFalse(validate(p,l,o))

 def test_three_product_cycle_and_restrictions(self):
  third=replace(self.p[0],sku='third',location='L2'); products=self.p+[third]
  target={'soft':'L1','strong':'L2','third':'L0'}
  plan=move_plan(products,self.l,target)
  self.assertTrue(plan['safe']); self.assertEqual(len(plan['steps']),4)
  self.l[3].case_weight_limit_kg=1
  self.assertFalse(move_plan(products,self.l,target)['safe'])
 def test_bad_history_and_route(self):
  self.assertTrue(validate(self.p,self.l,[replace(self.o[0],zone='wrong')]))
  self.assertTrue(validate(self.p,self.l,self.o+[self.o[0]]))
  self.assertTrue(validate(self.p,self.l,[replace(self.o[0],qty=0)]))
  self.l[0].route,self.l[1].route=self.l[1].route,self.l[0].route
  self.assertTrue(validate(self.p,self.l,self.o))
