#!/usr/bin/env python3
"""Chronological test of theatre importance for reconstructing a captured fleet.

Evaluate the actual snapshot theatre subset and reproducible random half-samples.
The target is captured AMC revenue, not national gross. Only earlier films train
weights; film-normalized revenue and shrinkage prevent blockbusters dominating.
This is a component experiment, not evidence of headline forecast improvement.
"""
import argparse, collections, json, random, statistics, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import predict as P


def fit_weights(groups, before):
    values=collections.defaultdict(list)
    films=collections.defaultdict(lambda:collections.defaultdict(list))
    for g in groups:
        if g['weekend_of']>=before or g['available_date']>=before:continue
        mean=statistics.mean(g['revenues'].values())
        if mean<=0:continue
        for name,v in g['revenues'].items():films[g['movie']][name].append(v/mean)
    for film in films.values():
        for name,vs in film.items():values[name].append(statistics.mean(vs))
    return {name:(len(vs)*statistics.median(vs)+5)/(len(vs)+5) for name,vs in values.items() if len(vs)>=3},len(films)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cache',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.cache.exists():groups=json.loads(args.cache.read_text())
    else:
        groups=[];h=json.load(open(Path(P.DATA_DIR)/'calibration.json'))['history']
        for w in sorted({e['weekend_of'] for e in h}):
            seats=P.load_seat_data(w);snaps=P.load_pre_reservation_data(w)
            for e in [e for e in h if e['weekend_of']==w and not e.get('data_outage')]:
                sd=P.movie_mapping_get(seats,e['movie'],{});sn=P.movie_mapping_get(snaps,e['movie'],{})
                for d,rs in sd.items():
                    if P._snapshot_day_name(d,rs) not in P.OPENING_WEEKEND_DAYS:continue
                    revenues=collections.defaultdict(float);latest=P._latest_seat_showtime_rows(rs)
                    for r in latest.values():
                        val=P.estimate_theatre_daily_revenue(r,{'calibration_factors':{}})
                        if val:revenues[val['theatre_name']]+=val['revenue']
                    if len(revenues)<250:continue
                    subset=sorted({r.get('theatre_name') for r in sn.get(d,[]) if r.get('theatre_name') in revenues})
                    groups.append({'movie':e['movie'],'weekend_of':w,'date':d,'available_date':e['date'],'revenues':dict(revenues),'snapshot_subset':subset})
            print(w,'groups',len(groups),flush=True);args.cache.write_text(json.dumps(groups))
    out=[]
    for g in groups:
        weights,n=fit_weights(groups,g['weekend_of'])
        if n<8:continue
        names=sorted(g['revenues']);rng=random.Random(g['movie']+g['date']);random_subset=rng.sample(names,len(names)//2)
        for label,subset in [('snapshot_subset',g['snapshot_subset']),('random_half',random_subset)]:
            if len(subset)<30 or len(subset)>.9*len(names):continue
            actual=sum(g['revenues'].values());observed=sum(g['revenues'][t] for t in subset)
            old=observed*len(names)/len(subset)
            new=observed*sum(weights.get(t,1) for t in names)/sum(weights.get(t,1) for t in subset)
            out.append({'movie':g['movie'],'weekend_of':g['weekend_of'],'date':g['date'],'sample':label,'actual':actual,'baseline':old,'weighted':new,'training_films':n})
    summary={}
    for era in ['development','later']:
        for sample in ['snapshot_subset','random_half']:
            rs=[r for r in out if (r['weekend_of']<'2026-08-01')==(era=='development') and r['sample']==sample]
            summary[era+'_'+sample]={'days':len(rs),'films':len({r['movie'] for r in rs})}
            if rs:
                for model in ['baseline','weighted']:
                    filmerrors=collections.defaultdict(list)
                    for r in rs:filmerrors[r['movie']].append(abs(r[model]/r['actual']-1)*100)
                    summary[era+'_'+sample][model+'_film_mape']=statistics.mean(statistics.mean(v) for v in filmerrors.values())
    args.output.write_text(json.dumps({'scope':__doc__,'summary':summary,'rows':out},indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
