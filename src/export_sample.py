"""Export the reproducible pilot and templates: python -m src.export_sample."""
from pathlib import Path
from dataclasses import replace
from .sample_data import sample
from .validation import csv_text

def main():
    dest=Path(__file__).resolve().parents[1]/'data'/'sample'; dest.mkdir(parents=True,exist_ok=True)
    p,l,o=sample()
    for kind,rows in [('products',p),('locations',l),('orders',o)]:
        (dest/f'{kind}.csv').write_text(csv_text(kind,rows),encoding='utf-8')
        (dest/f'{kind}_template.csv').write_text(csv_text(kind),encoding='utf-8')
    (dest/'infeasible_product.csv').write_text(csv_text('products',[replace(p[0],sku='OVERSIZE',location='',length_cm=200,locked=False)]),encoding='utf-8')
    print(f'Synthetic pilot exported to {dest}')

if __name__=='__main__':main()
