#!/usr/bin/env python3
"""Read-only checks for data defects that silently distort prediction training."""
import argparse,collections,csv,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from actuals_quality import independent_daily_actuals,estimated_actual_days
from historical_comps import load_movie_metadata,metadata_for_movie


def audit(data_dir):
    data_dir=Path(data_dir);history=json.loads((data_dir/'calibration.json').read_text())['history']
    with (data_dir/'movie-metadata.csv').open(newline='') as f:raw=list(csv.DictReader(f))
    metadata=load_movie_metadata(data_dir/'movie-metadata.csv');issues=[]
    for name,n in collections.Counter(r['movie'].casefold() for r in raw).items():
        if n>1:issues.append({'movie':name,'issue':'duplicate metadata','rows':n})
    for e in history:
        movie=e.get('movie');m=metadata_for_movie(movie,metadata)
        if not m or not m.audience_type:issues.append({'movie':movie,'issue':'missing audience classification'})
        if m and m.weekend_of!=e.get('weekend_of'):issues.append({'movie':movie,'issue':'metadata release date differs from training weekend','metadata':m.weekend_of,'training':e.get('weekend_of')})
        daily=independent_daily_actuals(e)
        if e.get('exclude_from_calibration'):issues.append({'movie':movie,'issue':'excluded from standard-opening calibration','reason':e.get('calibration_exclusion_reason','')})
        if len(daily)<4:issues.append({'movie':movie,'issue':'incomplete independent daily split','usable_days':sorted(daily),'estimated_days':sorted(estimated_actual_days(e)),'folded_previews':bool(e.get('previews_folded_into_friday'))})
        if len(daily)==4 and abs(sum(daily.values())-e.get('actual_total',0))>.05:
            issues.append({'movie':movie,'issue':'daily sum differs from weekend total','difference_m':round(sum(daily.values())-e['actual_total'],6)})
    return {'films':len(history),'complete_independent_splits':sum(len(independent_daily_actuals(e))==4 for e in history),'flagged_outages':sum(bool(e.get('data_outage')) for e in history),'issues':issues}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data-dir',type=Path,default=Path(__file__).resolve().parents[1]/'data');p.add_argument('--output',type=Path);a=p.parse_args();result=audit(a.data_dir);text=json.dumps(result,indent=2);print(text)
    if a.output:a.output.write_text(text+'\n')
if __name__=='__main__':main()
