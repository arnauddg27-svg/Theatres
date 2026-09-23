import copy,csv,json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
import actuals_quality as AQ
import calibrate as C
import historical_comps as HC
import predict as P
import theatre_weights as T
from calibration_backtest import earlier_history

class SourceTests(unittest.TestCase):
    def test_source_chart_resolves_country_suffix_and_decodes_entities(self):
        page='<a href="/movie/Some-and-Title-(2026-United-Kingdom)#tab=box-office">Some &amp; Title</a>'
        with patch.object(C.requests,'get',return_value=SimpleNamespace(status_code=200,text=page)):
            self.assertEqual('https://www.the-numbers.com/movie/Some-and-Title-(2026-United-Kingdom)',C.numbers_movie_urls('Some & Title','2026-08-21')[0])

    def test_ambiguous_chart_does_not_pick_a_random_remake(self):
        page='<a href="/movie/X-(2026)">X</a><a href="/movie/X-(1990)">X</a>'
        with patch.object(C.requests,'get',return_value=SimpleNamespace(status_code=200,text=page)):
            urls=C.numbers_movie_urls('X','2026-08-21')
        self.assertNotIn('https://www.the-numbers.com/movie/X-(1990)',urls)

    def test_article_moves_to_end_even_if_chart_unavailable(self):
        with patch.object(C.requests,'get',return_value=SimpleNamespace(status_code=403,text='')):
            self.assertEqual('https://www.the-numbers.com/movie/Sheep-Detectives-The-(2026)',C.numbers_movie_urls('The Sheep Detectives','2026-05-08')[0])

    def test_page_for_wrong_dates_does_not_stop_fallback(self):
        def page(date,rank,gross):return 'Daily Box Office Performance<table><tr><td>'+date+'</td><td>'+rank+'</td><td>'+gross+'</td></tr></table>'
        responses=[SimpleNamespace(status_code=200,text=page('May 8, 2025','1','$9,000,000')),SimpleNamespace(status_code=200,text=page('May&nbsp;7,&nbsp;2026','P','$1,000,000')[:-8]+'<tr><td>May 8, 2026</td><td>1</td><td>$4,000,000</td></tr></table>')]
        with patch.object(C,'numbers_movie_urls',return_value=['a','b']),patch.object(C.requests,'get',side_effect=responses):
            self.assertEqual({'Thursday':1,'Friday':3},C.fetch_movie_daily_history('X','2026-05-08'))

class RevisionTests(unittest.TestCase):
    def test_sourced_refresh_clears_stale_estimate_flags_and_keeps_revision(self):
        entry={'actual_source':'Friday split derived from seats','daily_actuals':{'Friday':5},'estimated_daily_actual_days':['Friday']}
        old=copy.deepcopy(entry)
        daily={'Thursday':1,'Friday':3,'Saturday':4,'Sunday':2}
        self.assertTrue(AQ.revise_reported_daily_actuals(entry,daily,'source URL','2026-09-19'))
        self.assertEqual(daily,AQ.independent_daily_actuals(entry))
        self.assertEqual(old,AQ.actuals_as_of(entry,'2026-09-01'))
        self.assertFalse(AQ.revise_reported_daily_actuals(entry,daily,'source URL','2026-09-19'))

    def test_sourced_refresh_rejects_incomplete_or_nonfinite_data(self):
        for daily in ({'Friday':5},{'Friday':5,'Saturday':float('nan'),'Sunday':2}):
            with self.assertRaises(ValueError):AQ.revise_reported_daily_actuals({},daily,'URL','2026-09-19')

    def test_unknown_previews_stay_excluded_after_refresh(self):
        entry={};AQ.revise_reported_daily_actuals(entry,{'Friday':4,'Saturday':3,'Sunday':2},'URL','2026-09-19')
        self.assertEqual({'Saturday':3,'Sunday':2},AQ.independent_daily_actuals(entry))

    def test_new_correction_cannot_enter_earlier_training_and_original_unchanged(self):
        old={'movie':'X','weekend_of':'2026-05-01','date':'2026-05-04','actual_total':10,'previews_folded_into_friday':True}
        new=dict(old,actual_total=11,actuals_revision={'as_of_date':'2026-09-19','previous':old})
        saved=copy.deepcopy(new)
        self.assertEqual(10,earlier_history([new],'2026-08-01')[0]['actual_total'])
        self.assertTrue(AQ.actuals_as_of(new,'2026-09-19')['previews_folded_into_friday'])
        self.assertEqual(11,earlier_history([new],'2026-09-20')[0]['actual_total'])
        self.assertEqual(saved,new)

    def test_multiple_revisions_walk_back_to_known_version(self):
        a={'actual_total':1};b={'actual_total':2,'actuals_revision':{'as_of_date':'2026-06-01','previous':a}}
        c={'actual_total':3,'actuals_revision':{'as_of_date':'2026-07-01','previous':b}}
        self.assertEqual(1,AQ.actuals_as_of(c,'2026-05-01')['actual_total'])
        self.assertEqual(2,AQ.actuals_as_of(c,'2026-06-15')['actual_total'])

    def test_metadata_append_does_not_erase_fields(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'m.csv';p.write_text('movie,genre,rating,national_theatre_count,amc_market_share_override\nX,animation,PG,4000,0.19\nX,,PG-13,,\n')
            row=HC.load_movie_metadata(p)['x']
            self.assertEqual('animation',row.genre);self.assertEqual('PG-13',row.rating)
            self.assertEqual(4000,row.national_theatre_count);self.assertEqual(.19,row.amc_market_share_override)

class WeightTests(unittest.TestCase):
    def profiles(self):return [{'movie':str(i),'weekend_of':'2026-01-02','available_date':'2026-01-05','weights':{'Big':2.,'Small':.5}} for i in range(8)]

    def test_future_films_and_duplicates_do_not_supply_training_support(self):
        ps=self.profiles();ps[0]['available_date']='2026-08-21'
        weights,n=T.fit(ps+[ps[1]],'2026-08-21');self.assertEqual(7,n);self.assertEqual({},weights)

    def test_weights_shrink_and_only_use_prior_films(self):
        ps=self.profiles();weights,n=T.fit(ps,'2026-08-21')
        self.assertEqual(8,n);self.assertAlmostEqual(21/13,weights['Big']);self.assertAlmostEqual(9/13,weights['Small'])

    def test_large_venues_need_less_expansion_than_count_ratio(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'p.json';p.write_text(json.dumps({'profiles':self.profiles()}))
            f,n=T.expansion(['Big'],['Big','Small'],2,'2026-08-20',p)
            self.assertLess(f,2);self.assertGreater(f,1);self.assertEqual(8,n)
            self.assertIsNone(T.expansion(['Unknown'],['Big','Small'],2,'2026-08-20',p))
            self.assertIsNone(T.expansion(['Big'],['Big','Small'],10,'2026-08-20',p))

    def test_new_config_venues_do_not_distort_historical_reference(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'p.json';p.write_text(json.dumps({'profiles':self.profiles()}))
            self.assertEqual(T.expansion(['Big'],['Big','Small'],2,'2026-08-20',p),T.expansion(['Big'],['Big','Small','New'],2,'2026-08-20',p))

class PresaleTests(unittest.TestCase):
    def test_snapshot_only_films_are_included_without_duplicate_aliases(self):
        self.assertEqual(['Existing: Film','New'],P.prediction_movie_names({'Existing: Film':{}},{'Existing Film':{},'New':{}}))

    def test_theatre_weight_experiment_stays_disabled(self):
        self.assertFalse(P.THEATRE_WEIGHTING_APPLY)

    def test_empty_data_remains_no_forecast(self):
        self.assertIsNone(P.predict_movie('X',{},[],{}))

    def test_future_rows_do_not_count_as_observed_days(self):
        pred={'movie':'X','seat_mid_m':0,'seat_low_m':0,'seat_high_m':0,
              'daily_details':{},'snapshot_days':list(P.OPENING_WEEKEND_DAYS),
              'snapshot_mid_m':20,'snapshot_low_m':18,'snapshot_high_m':22,
              'snapshot_model_coverage_ratio':1,'snapshot_calibration_support_factor':.4,
              'missing_data_profile':{'missing_days':list(P.OPENING_WEEKEND_DAYS)}}
        P.select_regression_prediction(pred)
        self.assertEqual(20,pred['regression_mid_m']);self.assertEqual('presales',pred['forecast_stage'])
        self.assertTrue(pred['forecast_provisional']);self.assertLessEqual(pred['regression_low_m'],10);self.assertGreaterEqual(pred['regression_high_m'],50)
        self.assertEqual({},pred['daily_details'])


class WindowTests(unittest.TestCase):
    def test_known_extended_windows_are_not_compared_to_four_calendar_days(self):
        from forecast_windows import window_profile
        self.assertFalse(window_profile('Minions & Monsters','2026-07-03')['market_window_compatible'])
        self.assertFalse(window_profile('The Mandalorian and Grogu','2026-05-22')['market_window_compatible'])
        self.assertTrue(window_profile('Film','2026-09-18')['market_window_compatible'])

    def test_rules_are_detected_even_without_an_extended_title(self):
        from forecast_windows import window_profile
        for field in ['description','notes','market_question','market_url']:
            with self.subTest(field=field):
                self.assertFalse(window_profile('New Film','2026-10-02',[{field:'The final 5-day opening weekend'}])['market_window_compatible'])

    def test_incompatible_market_has_no_distribution_edges_or_signals(self):
        import strategy
        pred={'regression_mid_m':50,'regression_low_m':40,'regression_high_m':60,'n_days':4,'n_theatres_total':425,'market_window_compatible':False}
        comparison=strategy.analyze_distribution('Film',pred,[{'question':'Will 5-day gross exceed $40M?','outcomePrices':'["0.1","0.9"]'}])
        self.assertEqual(0,comparison.confidence);self.assertEqual([],comparison.brackets)

    def test_non_preview_thursday_is_not_a_preview_training_label(self):
        import seat_regression as SR
        daily=AQ.ReportedDailyGrosses({'Thursday':10,'Friday':15,'Saturday':12,'Sunday':11},non_preview_thursday=True)
        entry={'movie':'Midweek'};AQ.revise_reported_daily_actuals(entry,daily,'URL','2026-09-19')
        self.assertNotIn('Thursday',AQ.independent_daily_actuals(entry));self.assertEqual([],SR.fitting_history([entry]))
        entry.pop('non_preview_thursday');entry.pop('exclude_from_calibration')
        self.assertTrue(AQ.revise_reported_daily_actuals(entry,daily,'URL','2026-09-19'))
        self.assertNotIn('Thursday',AQ.independent_daily_actuals(entry))
        self.assertFalse(AQ.revise_reported_daily_actuals(entry,daily,'URL','2026-09-19'))

class AvailabilityTests(unittest.TestCase):
    def test_preview_based_metadata_override_is_not_available_before_previews(self):
        from datetime import datetime,timezone
        meta=SimpleNamespace(amc_market_share_override=.193,amc_market_share_override_as_of='2026-06-19')
        self.assertIsNone(P.amc_market_share_override_for(meta,datetime(2026,6,18,16,tzinfo=timezone.utc)))
        self.assertIsNone(P.amc_market_share_override_for(meta))
        self.assertEqual(.193,P.amc_market_share_override_for(meta,datetime(2026,6,20,16,tzinfo=timezone.utc)))


if __name__ == "__main__":
    unittest.main()
