#!/usr/bin/env python3
"""Test a learned reservation-growth curve on earlier-film matched showtimes.

Research only: this candidate did not improve the later-weekend evaluation
and is NOT used in production. Unit is seats at the same show, not dollars.
One observation per show and lead bucket prevents repeated scrapes from
multiplying a show's influence. Fit only on earlier, already-recorded films.
"""
import argparse,sys,json,collections,statistics,math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import predict as P
from forecast_evaluation import utc_timestamp

def bucket(m):
 for hours in [1,3,6,24,48,96]:
  if m<=hours*60:return hours


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=Path, required=True, help='Reusable matched-showtime cache')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    path = args.pairs
    path.parent.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
     history=json.load(open(Path(P.DATA_DIR)/'calibration.json'))['history'];groups=[]
     for w in sorted({h['weekend_of'] for h in history}):
      seats=P.load_seat_data(w);snaps=P.load_pre_reservation_data(w)
      for h in [h for h in history if h['weekend_of']==w and not h.get('data_outage')]:
       movie=h['movie'];ss=[r for rs in P.movie_mapping_get(seats,movie,{}).values() for r in rs]
       final=P._latest_seat_showtime_rows([r for r in ss if P._parse_numeric(r.get('minutes_after_showtime'),-1)>=0])
       latest={}
       for rs in P.movie_mapping_get(snaps,movie,{}).values():
        for r in rs:
         lead=P._parse_numeric(r.get('minutes_until_showtime'),-1);b=bucket(lead)
         key=P._showtime_match_key(r);end=final.get(key)
         if lead<=0 or not b or not end:continue
         before=utc_timestamp(r.get('snapshot_time'));after=utc_timestamp(end.get('check_time'))
         if not before or not after or before>=after:continue
         cap=P._parse_numeric(r.get('total_seats'));ecap=P._parse_numeric(end.get('total_seats'))
         reserved=P._parse_numeric(r.get('reserved_seats'),-1);sold=P._parse_numeric(end.get('seats_sold'),-1)
         if cap!=ecap or cap<=0 or not(0<=reserved<=cap and 0<=sold<=cap):continue
         prev=latest.get((key,b))
         if not prev or before>prev[0]:latest[(key,b)]=(before,[reserved,cap,sold,lead])
       by=collections.defaultdict(list)
       for (_,b),(_,vals) in latest.items():by[b].append(vals)
       for b,vals in by.items():
        if len(vals)>=30:groups.append({'movie':movie,'weekend_of':w,'actual_recorded':h['date'],'bucket':b,'pairs':vals})
       print(w,movie,len(latest),flush=True)
      path.write_text(json.dumps(groups))
    else:groups=json.loads(path.read_text())

    def predict(group,prior):
     b=group['bucket']; default=P.snapshot_reservation_multiplier(b*60)
     ratios=[]
     for g in prior:
      if g['bucket']!=b:continue
      reserved=sum(r[0] for r in g['pairs']);sold=sum(r[2] for r in g['pairs'])
      if reserved>0:ratios.append(sold/reserved)
     # Film-balanced multiplicative shrinkage; no tuning on held-out months.
     if len(ratios)<5:return default
     shrink=len(ratios)/(len(ratios)+8)
     return max(1,min(8, math.exp((1-shrink)*math.log(default)+shrink*statistics.median(math.log(max(.1,r)) for r in ratios))))

    out=[]
    for g in groups:
     prior=[t for t in groups if t['weekend_of']<g['weekend_of'] and t['actual_recorded']<g['weekend_of']]
     if len({t['movie'] for t in prior})<8:continue
     factor=predict(g,prior);actual=sum(r[2] for r in g['pairs'])
     if actual<=0:continue
     old=sum(min(cap,res*P.snapshot_reservation_multiplier(lead)) for res,cap,sold,lead in g['pairs'])
     new=sum(min(cap,res*factor) for res,cap,sold,lead in g['pairs'])
     out.append({'movie':g['movie'],'weekend_of':g['weekend_of'],'bucket':g['bucket'],'actual':actual,'old':old,'new':new,'factor':factor})
    for label,rs in [('development',[r for r in out if r['weekend_of']<'2026-08-01']),('holdout',[r for r in out if r['weekend_of']>='2026-08-01'])]:
     print(label,len(rs),len({r['movie'] for r in rs}))
     for k in ['old','new']:
      print(k,'WAPE',100*sum(abs(r[k]-r['actual']) for r in rs)/sum(r['actual'] for r in rs),'MAPE',statistics.mean(abs(r[k]/r['actual']-1)*100 for r in rs))
    args.output.write_text(json.dumps(out,indent=2))


if __name__ == "__main__":
    main()
