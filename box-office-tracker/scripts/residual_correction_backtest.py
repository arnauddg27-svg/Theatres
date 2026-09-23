#!/usr/bin/env python3
"""Exploratory corrections using only earlier films; not enabled in production."""
import argparse,collections,copy,json,math,statistics,sys
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(REPO),str(REPO/'scripts')]
parser=argparse.ArgumentParser(description="Research only: compare sequential residual corrections on an accuracy_backtest replay cache. No model setting is changed.")
parser.add_argument('--replays',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
import seat_regression as SR
from actuals_quality import actuals_as_of
R=json.loads(args.replays.read_text())['rows'];H=json.loads((REPO/'data/calibration.json').read_text())['history'];H={h['movie']:h for h in H}
R=[r for r in R if r.get('unweighted') and not r.get('data_outage') and r['training_movies']>=8]

def key(r):return r['unweighted']['forecast_stage']
def clip(x,lo=-.7,hi=.7):return min(hi,max(lo,x))
def y(r,weekend):
 h=actuals_as_of(H[r['movie']],weekend)
 return clip(math.log(h['actual_total']/r['unweighted']['regression_mid_m']))
def features(r,kind):
 p=r['unweighted'];st=key(r);mid=p['regression_mid_m'];a=p.get('audience_type','')
 if kind=='stage_bias':return [1,int(st=='presales'),int(st=='after-previews'),int(st=='after-friday')]
 x=[1,clip(math.log(mid/25),-2,2),(p.get('seat_missing_day_share') or 0),1-(p.get('coverage_ratio') or 0)]
 if kind=='audience_ridge':x += [int(a=='broad_family'),int(a=='fan_driven'),int(a=='young_male'),int(a=='adult_drama')]
 return x

def train_rows(r):
 # At most one row per film and forecast stage; older versions restored as known.
 eligible=[t for t in R if t['weekend_of']<r['weekend_of'] and H[t['movie']].get('date','9999')<r['weekend_of'] and not actuals_as_of(H[t['movie']],r['weekend_of']).get('exclude_from_calibration')]
 return eligible

def candidate(r,kind,prior):
 ts=train_rows(r);p=r['unweighted'];base=p['regression_mid_m']
 if kind=='same_stage':
  ts=[t for t in ts if key(t)==key(r)]
  grouped=collections.defaultdict(list)
  for t in ts:grouped[t['movie']].append(y(t,r['weekend_of']))
  vals=[statistics.mean(v) for v in grouped.values()]
  if len(vals)<8:return base
  bias=statistics.median(vals)*len(vals)/(len(vals)+prior)
 elif kind=='same_audience':
  ts=[t for t in ts if t['unweighted'].get('audience_type')==p.get('audience_type')]
  grouped=collections.defaultdict(list)
  for t in ts:grouped[t['movie']].append(y(t,r['weekend_of']))
  vals=[statistics.mean(v) for v in grouped.values()]
  if len(vals)<5:return base
  bias=statistics.median(vals)*len(vals)/(len(vals)+prior)
 else:
  count=collections.Counter(t['movie'] for t in ts)
  if len(count)<8:return base
  X=[features(t,kind) for t in ts];Y=[y(t,r['weekend_of']) for t in ts];ws=[1/count[t['movie']] for t in ts]
  b=SR.weighted_ridge(X,Y,ws,[0]*len(X[0]),[1]*len(X[0]),prior)
  bias=sum(u*v for u,v in zip(b,features(r,kind))) if b else 0
 return base*math.exp(clip(bias,-.25,.25))

def summary(rows,name):
 rs=[r for r in rows if r['unweighted']['forecast_stage']!='presales'];film=collections.defaultdict(list)
 for r in rs:
  val=r['unweighted']['regression_mid_m'] if name=='baseline' else r['experiments'][name]
  film[r['movie']].append(abs(val/r['actual_m']-1)*100)
 return {'forecasts':len(rs),'films':len(film),'mape_pct':round(statistics.mean(x for vs in film.values() for x in vs),3),'film_mape_pct':round(statistics.mean(statistics.mean(vs) for vs in film.values()),3)}
settings=[('same_stage',8),('same_audience',8),('stage_bias',8),('scale_ridge',8),('audience_ridge',8),('audience_ridge',32)]
for r in R:r['experiments']={f'{kind}_{prior}':candidate(r,kind,prior) for kind,prior in settings}
result={'scope':'Exploratory sequential residual corrections; target-film and same-week outcomes excluded; each training film has equal total weight. Only earlier available label revisions. No experiment automatically enabled. Reused periods, not fresh holdouts.','summary':{},'rows':[{k:r[k] for k in ['movie','weekend_of','checkpoint','actual_m','experiments']}|{'baseline_m':r['unweighted']['regression_mid_m']} for r in R]}
for label,rs in [('development',[r for r in R if r['weekend_of']<'2026-08-01']),('later',[r for r in R if r['weekend_of']>='2026-08-01'])]:
 result['summary'][label]={name:summary(rs,name) for name in ['baseline']+[f'{kind}_{prior}' for kind,prior in settings]}
print(json.dumps(result['summary'],indent=2));args.output.write_text(json.dumps(result,indent=2)+'\n')
