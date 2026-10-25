"""Grocery slotting decision support. Launch from repository root with Streamlit."""
import sys
import json
from pathlib import Path
from dataclasses import asdict
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import streamlit as st
from src.models import Product,Config
from src.sample_data import sample
from src.validation import validate,csv_text,read_csv
from src.evaluation import compare,frequencies,sequence
from src.optimization import optimize,place_new
from src.persistence import Store,snapshot,restore
from src.movement import move_plan

ROOT=Path(__file__).resolve().parents[1]

def table(rows): return pd.DataFrame([asdict(x) for x in rows])

def main():
    st.set_page_config(page_title='Grocery Slotting | QA',layout='wide')
    st.title('Grocery slotting decisions')
    st.caption('Zone 1 pilot • Decision support for QA • Godwin Osayamwen')
    st.warning('Sequence scores are proxies, not physical pallet simulations or predictions of damage. All recommendations require QA review.')
    if 'dataset' not in st.session_state:
        c=Config(); p,l,o=sample(c); st.session_state.dataset=(p,l,o,c,{x.sku:x.location for x in p})
    p,l,o,c,a=st.session_state.dataset
    page=st.sidebar.radio('Workspace',['Overview','Place a New Product','Improve Existing Positions','Follow a Sample Assignment','QA Review and Move Plan','Data and Validation','Stakeholder Brief'])
    st.sidebar.caption('Synthetic data: 63 grocery cases; 30 days. No WMS or Vocollect connection.')
    base={x.sku:x.location for x in p if x.location}
    if page=='Overview':
        st.write('Products already belong to approved zones. QA can improve where cases are collected so strong supporting cases tend to precede vulnerable cases within a zone assignment. Pallets leave for wrapping and shipping after that assignment.')
        if all(x.sku in base for x in o):
            result=compare(p,l,o,base,a,c)
            st.dataframe(pd.DataFrame(result).T,use_container_width=True)
            st.caption('Lower sequence proxy is preferred. Both columns use identical order lines (workload hash shown). Travel is illustrative front-entry/front-exit, ascending bay visits; timing uses assumptions below.')
        st.json(asdict(c))
        st.write('No claims of safety, damage reduction, productivity gains or savings are established by these estimates.')
    elif page=='Improve Existing Positions':
        with st.form('priorities'):
            penalty=st.number_input('Penalty per relocated product',0.,1.,c.move_penalty,step=.001)
            tw=st.number_input('Weight for illustrative meters per order line',0.,1.,float(c.travel_weight),step=.001)
            if st.form_submit_button('Find feasible improvements'):
                c.move_penalty=penalty; c.travel_weight=tw
                with st.spinner('Evaluating vacancies, swaps and bounded cycles'):
                    r=optimize(p,l,o,c)
                a=r['assignment']; st.session_state.dataset=(p,l,o,c,a); st.session_state.result=r
        if 'result' in st.session_state:
            r=st.session_state.result; st.info(r['status']); st.json({k:v for k,v in r.items() if k not in ('assignment','plan')})
        cols=st.columns(2)
        for col,label,layout in [(cols[0],'Current aisle map',base),(cols[1],'Proposed aisle map',a)]:
            rows=[]; inv={v:k for k,v in layout.items()}; ps={x.sku:x for x in p}
            for loc in sorted(l,key=lambda x:x.route):
                sku=inv.get(loc.location_id,'EMPTY'); prod=ps.get(sku)
                rows.append({'aisle':loc.aisle,'bay':loc.bay,'route':loc.route,'slot':loc.location_id,'SKU':sku,'description':prod.description if prod else '', 'locked':loc.locked or bool(prod and prod.locked)})
            col.subheader(label); col.dataframe(rows,height=450,use_container_width=True)
        moves=[{'SKU':s,'from':base.get(s,'NEW'),'to':d,'reason':'Selected feasible objective improvement; supporting/vulnerable case co-occurrence balanced against move penalty'} for s,d in a.items() if base.get(s)!=d]
        st.dataframe(moves)
        for row in moves:
            prod=next(x for x in p if x.sku==row['SKU'])
            st.caption(f"{prod.description}: {prod.packaging}; support {prod.support:.2f}, crushability {prod.crushability:.2f}, case {prod.weight_kg:g} kg. {row['from']} to {row['to']}; see matched assignment sequence to review co-picked products.")
    elif page=='Place a New Product':
        with st.form('new'):
            sku=st.text_input('SKU','NEW-001'); desc=st.text_input('Description','New grocery case'); category=st.text_input('Category','Beverage'); zone=st.text_input('Approved zone','Zone 1')
            weight=st.number_input('Case weight (kg)',.1,1000.,12.)
            dims=[st.number_input(f'Case {x} (cm)',.1,500.,v) for x,v in [('length',40.),('width',30.),('height',28.)]]
            pack=st.selectbox('Packaging',['carton','rigid jug','tray','shrink wrap','bag','fragile carton'])
            support=st.slider('Base/support suitability',0.,1.,.7); crush=st.slider('Crushability',0.,1.,.3)
            top=st.number_input('Maximum supported top case weight (kg)',0.,1000.,20.)
            stock=st.number_input('Required pick-face cases',1,10000,4); levels=st.text_input('Allowed levels, separated by |','1')
            freq=st.number_input('Expected line frequency over comparable 30 days (assumption)',0.,10000.,20.)
            depth=st.selectbox('Maximum existing-product displacements',[0,1,2,3],index=1)
            submitted=st.form_submit_button('Rank placement options')
        if submitted:
            new=Product(sku,desc,category,zone,weight,*dims,pack,support,crush,top,expected_frequency=freq,required_stock=stock,allowed_levels=levels)
            try:
                r=place_new(new,p,l,o,c,depth); st.session_state.placement=(new,r)
            except ValueError as e: st.error(str(e))
        if 'placement' in st.session_state:
            new,r=st.session_state.placement; st.info(r['status']); st.caption(f"Bounded search: {r['candidate_checks']} checks / {r['search_limit']}. Cold-start frequency is assumed; no historical co-occurrence is invented.")
            for i,opt in enumerate(r['options']):
                with st.expander(f"{i+1}. {opt['location']} | {opt['existing_moves']} existing products move"):
                    st.write(opt['explanation']); st.dataframe(opt['plan']['steps'])
                    if st.button('Use as draft scenario',key=f'option{i}'):
                        st.session_state.dataset=(p+[new],l,o,c,opt['assignment']); st.session_state.pop('placement',None); st.rerun()
    elif page=='Follow a Sample Assignment':
        ids=sorted({(x.date,x.assignment_id) for x in o}); selected=st.selectbox('Assignment (one zone pallet)',ids)
        lines=[x for x in o if (x.date,x.assignment_id)==selected]
        ps={x.sku:x for x in p}
        for col,label,layout in zip(st.columns(2),['Before collection order','After collection order'],[base,a]):
            col.subheader(label); col.dataframe([{'pick':i+1,'SKU':x.sku,'description':ps[x.sku].description,'cases':x.qty,'slot':layout[x.sku],'support':ps[x.sku].support,'crushability':ps[x.sku].crushability} for i,x in enumerate(sequence(lines,layout,l))])
        st.write('The same products and quantities follow explicit route sequence. Earlier supporting cases may improve the proxy. This illustration does not model layers, placement orientation, total top load or physical stability.')
    elif page=='QA Review and Move Plan':
        (ROOT/'data').mkdir(exist_ok=True); store=Store(ROOT/'data'/'scenarios.sqlite3')
        plan=move_plan(p,l,a)
        st.info('Approval records a local decision only. It does not execute moves or change Vocollect/WMS.')
        st.write('Local SQLite is not enterprise authentication or a production approval system. Reviewer names are self-reported.')
        if not plan['safe']: st.error('; '.join(plan['errors']))
        st.dataframe(plan['steps']); st.download_button('Download action list',pd.DataFrame(plan['steps']).to_csv(index=False),'move_plan.csv')
        name=st.text_input('Scenario name','Zone 1 QA candidate')
        if st.button('Save immutable draft'):
            st.session_state.sid=store.save(name,snapshot(p,l,o,c,a)); st.success('Draft saved')
        choices=store.list()
        if choices:
            sid=st.selectbox('Saved scenario',choices,format_func=lambda x:f'{x[0]}: {x[1]}')[0]
            payload=store.load(sid); st.download_button('Export selected scenario JSON',json.dumps(payload,indent=2),'scenario.json')
            if st.button('Load selected scenario'):
                st.session_state.dataset=restore(payload); st.rerun()
            st.dataframe(store.history(sid),column_config={0:'Status',1:'Reviewer',2:'Notes',3:'UTC timestamp'})
            with st.form('review'):
                status=st.selectbox('Next review state',['reviewed','approved','rejected']); reviewer=st.text_input('Reviewer'); notes=st.text_area('Review notes')
                if st.form_submit_button('Record decision'):
                    try: store.review(sid,status,reviewer,notes); st.success('Decision recorded for saved scenario')
                    except ValueError as e: st.error(str(e))
        store.db.close()
    elif page=='Data and Validation':
        st.write('Import all three CSVs together. Validation is atomic: any error keeps the current dataset. Templates include all columns; booleans use true/false. Stock capacity and rack limits are declared values, not inferred from case volume.')
        uploads={}
        search=st.text_input('Search master tables')
        for kind,rows in [('products',p),('locations',l),('orders',o)]:
            with st.expander(kind.title()):
                st.download_button('Download template',csv_text(kind),f'{kind}_template.csv',key=f't{kind}')
                st.download_button('Download data',csv_text(kind,rows),f'{kind}.csv',key=f'd{kind}')
                uploads[kind]=st.file_uploader(f'{kind} CSV',type='csv')
                df=table(rows)
                if search: df=df[df.astype(str).apply(lambda x:x.str.contains(search,case=False,regex=False)).any(axis=1)]
                st.dataframe(df)
        if st.button('Validate and load CSV bundle'):
            if not all(uploads.values()): st.error('Select products, locations and orders CSVs')
            else:
                parsed={}; errors=[]
                for kind,f in uploads.items():
                    try: parsed[kind],err=read_csv(kind,f.getvalue().decode('utf-8-sig')); errors+=err
                    except UnicodeError: errors.append(f'{kind}: UTF-8 required')
                if not errors: errors=validate(parsed['products'],parsed['locations'],parsed['orders'])
                if not errors:
                    try:
                        pp,ll,oo=parsed['products'],parsed['locations'],parsed['orders']; aa={x.sku:x.location for x in pp if x.location}
                        restore(snapshot(pp,ll,oo,c,aa)); st.session_state.dataset=(pp,ll,oo,c,aa); st.rerun()
                    except ValueError as e: errors.append(str(e))
                for error in errors: st.error(error)
        st.subheader('Observed picking frequency and case velocity'); st.dataframe(pd.DataFrame(frequencies(o)).T)
        with st.form('config'):
            aisles=st.text_input('Aisle route order',c.aisle_order); start=st.number_input('Lowest bay',0,1000,c.start_number); end=st.number_input('Highest bay',0,1000,c.end_number)
            spacing=st.number_input('Illustrative bay spacing (m)',.1,100.,c.bay_spacing_m); aisle_space=st.number_input('Illustrative aisle spacing (m)',.1,100.,c.aisle_spacing_m)
            speed=st.number_input('Assumed walking speed (m/s)',.1,5.,c.walking_mps); handling=st.number_input('Assumed handling seconds/case',0.,300.,float(c.handling_seconds))
            if st.form_submit_button('Generate fresh synthetic pilot with configuration'):
                cc=Config(aisles,start,end,spacing,aisle_space,speed,handling,c.move_penalty,c.travel_weight)
                try:
                    pp,ll,oo=sample(cc); st.session_state.dataset=(pp,ll,oo,cc,{x.sku:x.location for x in pp}); st.rerun()
                except ValueError as e: st.error(str(e))
        imported=st.file_uploader('Import scenario JSON',type='json')
        if imported and st.button('Validate and load scenario'):
            try: st.session_state.dataset=restore(json.loads(imported.getvalue())); st.rerun()
            except (ValueError,KeyError,TypeError) as e: st.error(f'Invalid scenario: {e}')
        st.write('Infeasible example: change a case to 200 cm long, 100 kg or an unapproved zone; placement must fail.')
    else:
        text=(ROOT/'docs'/'stakeholder_brief.md').read_text(encoding='utf-8'); st.markdown(text); st.download_button('Download printable stakeholder brief',text,'stakeholder_brief.md')

if __name__=='__main__': main()
