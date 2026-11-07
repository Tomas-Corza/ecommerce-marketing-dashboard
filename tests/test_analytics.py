import unittest
import pandas as pd
from src.analytics import normalize_sales,normalize_ads,summarize,campaign_table,daily_table,filter_dates

class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.sales=normalize_sales(pd.DataFrame([{'date':'2026-01-01','orders':10,'revenue':1000,'new_customers':4},{'date':'2026-01-02','orders':5,'revenue':500,'new_customers':2}]))
        self.ads=normalize_ads(pd.DataFrame([{'date':'2026-01-01','platform':'Google Ads','campaign':'Brand','spend':100,'attributed_revenue':400,'attributed_orders':4,'attributed_new_customers':2},{'date':'2026-01-02','platform':'Meta Ads','campaign':'Prospecting','spend':200,'attributed_revenue':300,'attributed_orders':3,'attributed_new_customers':1}]))
    def test_metrics(self):
        k=summarize(self.sales,self.ads)
        self.assertEqual(k['revenue'],1500)
        self.assertEqual(k['aov'],100)
        self.assertEqual(k['mer'],5)
        self.assertEqual(k['blended_cac'],50)
        self.assertAlmostEqual(k['platform_roas'],7/3)
    def test_campaign_table(self):
        c=campaign_table(self.ads)
        self.assertEqual(len(c),2)
        self.assertEqual(c.iloc[0]['campaign'],'Prospecting')
        self.assertEqual(c.iloc[0]['roas'],1.5)
    def test_missing_columns(self):
        with self.assertRaises(ValueError): normalize_sales(pd.DataFrame({'date':['2026-01-01']}))
    def test_empty_ads_safe(self):
        k=summarize(self.sales,self.ads.iloc[0:0])
        self.assertIsNone(k['mer'])
        self.assertIsNone(k['platform_roas'])
    def test_filter_inclusive(self):
        filtered=filter_dates(self.sales,'2026-01-02','2026-01-02')
        self.assertEqual(len(filtered),1)
        self.assertEqual(filtered.iloc[0]['revenue'],500)
    def test_daily_merge(self):
        t=daily_table(self.sales,self.ads)
        self.assertEqual(len(t),2)
        self.assertEqual(t['spend'].sum(),300)
    def test_negative_rejected(self):
        bad=self.ads.copy();bad.loc[0,'spend']=-1
        with self.assertRaises(ValueError): normalize_ads(bad)

if __name__=='__main__': unittest.main()
