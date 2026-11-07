"""Pure, testable ecommerce marketing calculations (USD)."""
import pandas as pd

SALES_COLUMNS = {'date','orders','revenue','new_customers'}
ADS_COLUMNS = {'date','platform','campaign','spend','attributed_revenue','attributed_orders','attributed_new_customers'}

def normalize_sales(df):
    missing = SALES_COLUMNS - set(df.columns)
    if missing: raise ValueError(f"Sales CSV missing columns: {', '.join(sorted(missing))}")
    out=df.copy()
    out['date']=pd.to_datetime(out['date'],errors='coerce').dt.normalize()
    for col in ('orders','revenue','new_customers'):
        out[col]=pd.to_numeric(out[col],errors='coerce')
    if out[['date','orders','revenue','new_customers']].isna().any().any():
        raise ValueError('Sales data has invalid dates or numeric values.')
    if (out[['orders','revenue','new_customers']]<0).any().any():
        raise ValueError('Sales values must be nonnegative.')
    if (out['new_customers']>out['orders']).any():
        raise ValueError('new_customers cannot exceed orders in this simplified dataset.')
    return out

def normalize_ads(df):
    missing = ADS_COLUMNS - set(df.columns)
    if missing: raise ValueError(f"Ads CSV missing columns: {', '.join(sorted(missing))}")
    out=df.copy()
    out['date']=pd.to_datetime(out['date'],errors='coerce').dt.normalize()
    for col in ('spend','attributed_revenue','attributed_orders','attributed_new_customers'):
        out[col]=pd.to_numeric(out[col],errors='coerce')
    if out[list(ADS_COLUMNS)].isna().any().any():
        raise ValueError('Ads data contains blank or invalid required values.')
    if (out[['spend','attributed_revenue','attributed_orders','attributed_new_customers']]<0).any().any():
        raise ValueError('Ad amounts must be nonnegative.')
    if out[['platform','campaign']].astype(str).apply(lambda s:s.str.strip().eq('')).any().any():
        raise ValueError('Platform and campaign cannot be blank.')
    return out

def safe_div(n,d):
    return float(n)/float(d) if d else None

def summarize(sales,ads):
    revenue=float(sales['revenue'].sum())
    orders=float(sales['orders'].sum())
    customers=float(sales['new_customers'].sum())
    spend=float(ads['spend'].sum())
    attributed=float(ads['attributed_revenue'].sum())
    attributed_customers=float(ads['attributed_new_customers'].sum())
    return {'revenue':revenue,'orders':int(orders),'new_customers':int(customers),
            'spend':spend,'aov':safe_div(revenue,orders),
            'mer':safe_div(revenue,spend), 'blended_cac':safe_div(spend,customers),
            'platform_roas':safe_div(attributed,spend),
            'platform_cac':safe_div(spend,attributed_customers)}

def campaign_table(ads):
    if ads.empty:
        return pd.DataFrame(columns=['platform','campaign','spend','attributed_revenue','attributed_orders','attributed_new_customers','roas','cac','cpa'])
    grouped=ads.groupby(['platform','campaign'],as_index=False)[['spend','attributed_revenue','attributed_orders','attributed_new_customers']].sum()
    grouped['roas']=grouped.apply(lambda r:safe_div(r['attributed_revenue'],r['spend']),axis=1)
    grouped['cac']=grouped.apply(lambda r:safe_div(r['spend'],r['attributed_new_customers']),axis=1)
    grouped['cpa']=grouped.apply(lambda r:safe_div(r['spend'],r['attributed_orders']),axis=1)
    return grouped.sort_values('spend',ascending=False).reset_index(drop=True)

def daily_table(sales,ads):
    s=sales.groupby('date',as_index=False)[['revenue','orders','new_customers']].sum()
    a=ads.groupby('date',as_index=False)[['spend','attributed_revenue']].sum()
    daily=s.merge(a,on='date',how='outer').fillna(0).sort_values('date')
    daily['mer']=daily.apply(lambda r:safe_div(r['revenue'],r['spend']),axis=1)
    return daily

def filter_dates(df,start,end):
    dt=pd.to_datetime(df['date'])
    return df.loc[(dt>=pd.Timestamp(start)) & (dt<=pd.Timestamp(end))].copy()
