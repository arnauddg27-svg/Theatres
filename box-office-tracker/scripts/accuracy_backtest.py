#!/usr/bin/env python3
"""Reconstruct stage forecasts with strict capture times and versioned labels.

Compare theatre weighting on identical inputs. Metadata/prices are current
references, so this is a reconstruction, not a claim of historical live accuracy.
Earlier revisions, same-week actuals, unknown publication times and future
captures are withheld. Both candidates have exactly the same forecast coverage.
"""
import argparse,copy,json,sys,statistics,collections
from datetime import timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import stage_backtest as B
P=B.P


def summary(rows,key):
    rs=[r for r in rows if r.get(key) and not r.get('data_outage') and r['training_movies']>=8]
    films=collections.defaultdict(list)
    for r in rs:films[r['movie']].append(abs(r[key]['regression_mid_m']/r['actual_m']-1)*100)
    if not rs:return {'forecasts':0}
    return {'forecasts':len(rs),'films':len(films),'mape_pct':statistics.mean(x for xs in films.values() for x in xs),'film_mape_pct':statistics.mean(statistics.mean(xs) for xs in films.values()),'coverage_pct':100*statistics.mean(r[key]['regression_low_m']<=r['actual_m']<=r[key]['regression_high_m'] for r in rs)}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    history=json.load(open(Path(P.DATA_DIR)/'calibration.json'))['history'];counts=P.load_theatre_counts();metadata=P.load_movie_metadata();out=[]
    for w in sorted({e['weekend_of'] for e in history}):
        try:cal=P.load_calibration_freeze(P.DATA_DIR,w)
        except FileNotFoundError:cal={'history':[],'calibration_factors':{}}
        cal['history']=B.earlier_history(history,w)
        cal=P.sanitize_calibration(cal,P.DAY_WEIGHTS_DEFAULT,P.DEFAULT_AMC_MARKET_SHARE)
        seats=P.load_seat_data(w);snaps=P.load_pre_reservation_data(w)
        for name,offset in B.CHECKPOINTS.items():
            cutoff=B.checkpoint_time(w,offset);prior=(cutoff.astimezone(B.ET).date()-timedelta(days=1)).isoformat()
            ss=B.filter_captured(seats,cutoff,'check_time');sn=B.filter_captured(snaps,cutoff,'snapshot_time')
            overrides=P.load_daily_actual_overrides(w,through_date=prior)
            overrides={m:{d:v for d,v in days.items() if v.get('as_of_date')} for m,days in overrides.items()}
            for e in [e for e in history if e['weekend_of']==w]:
                movie=e['movie'];sd=P.movie_mapping_get(ss,movie,{});sp=P.movie_mapping_get(sn,movie,{})
                row={k:e.get(k) for k in ('movie','weekend_of','data_outage')};row.update(checkpoint=name,actual_m=e['actual_total'],training_movies=len(cal['history']),cutoff=cutoff.isoformat())
                for key,weighted in [('unweighted',False),('weighted',True)]:
                    P.THEATRE_WEIGHTING_APPLY=weighted
                    pred=P.predict_movie(movie,sd,[],copy.deepcopy(cal),snapshot_data=sp,social_data={},daily_actual_overrides=overrides,showtime_link_profiles={},reviews_data={},cross_chain_data={},national_theatre_count=P.national_theatre_count_for_movie(movie,counts,metadata=metadata))
                    row[key]=pred
                out.append(row)
                print(w,name,movie,*[round(row[k]['regression_mid_m'],2) if row[k] else None for k in ['unweighted','weighted']],flush=True)
        args.output.write_text(json.dumps({'scope':__doc__,'rows':out},default=str))
    result={}
    for label,rs in [('development',[r for r in out if r['weekend_of']<'2026-08-01']),('later',[r for r in out if r['weekend_of']>='2026-08-01'])]:
        for stage in ['regular','presales']:
            group=[r for r in rs if r.get('unweighted') and (r['unweighted']['forecast_stage']=='presales')==(stage=='presales')]
            result[label+'_'+stage]={key:summary(group,key) for key in ['unweighted','weighted']}
    args.output.write_text(json.dumps({'scope':__doc__,'summary':result,'rows':out},default=str));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
