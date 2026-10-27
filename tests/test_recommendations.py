import unittest
from dataclasses import replace
from src.models import Product, Location
from src.optimization import place_new
from src.evaluation import pallet_stability_proxy
from src.validation import validate

class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.slots=[Location(f'S{i}', 'Z', 'D3',i+1,1,i) for i in range(5)]
        self.water=Product('water','Water','Beverage','Z',20,42,28,26,
                           support=.9,crushability=.1,max_top_kg=40,location='S2')
        self.chips=Product('chips','Chips','Snack','Z',2,55,38,42,
                           support=.1,crushability=.95,max_top_kg=2,location='S3')
    def test_fragile_incoming_ranks_after_heavy(self):
        incoming=replace(self.chips,sku='new',location='')
        r=place_new(incoming,[self.water],self.slots,[],max_depth=0)
        self.assertGreater(self.slots[int(r['options'][0]['location'][1:])].route,2)
        for option in r['options']:
            self.assertAlmostEqual(option['rank_cost'],sum(option['score_components'].values()))
            self.assertFalse(validate([self.water,incoming],self.slots,assignment=option['assignment']))
    def test_heavy_incoming_ranks_before_fragile(self):
        r=place_new(replace(self.water,sku='new',location=''),[self.chips],self.slots,[],max_depth=0)
        self.assertLess(int(r['options'][0]['location'][1:]),3)
    def test_declared_route_used_in_stability(self):
        slots=[replace(self.slots[0],location_id='Z'),replace(self.slots[1],location_id='A')]
        water=replace(self.water,location='Z'); chips=replace(self.chips,location='A')
        result=pallet_stability_proxy([water,chips],locations=slots)
        self.assertEqual(result['heavy_after_fragile'],0)
    def test_locked_vacancy_is_never_offered(self):
        self.slots[0].locked=True
        options=place_new(replace(self.water,sku='new',location=''),[],self.slots,[])['options']
        self.assertTrue(options)
        self.assertTrue(all(o['location']!='S0' for o in options))
