"""Streamlit dashboard using fictional data or user-supplied CSV exports."""
from pathlib import Path
import pandas as pd
import streamlit as st
from src.analytics import normalize_sales,normalize_ads,filter_dates,summarize,campaign_table,daily_table

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='E-commerce Marketing Dashboard',page_icon='📈',layout='wide')
st.title("E-commerce Marketing Dashboard")

st.markdown("**Developed by Tomas Corza**")

st.write(
    "An interactive Python dashboard for analyzing e-commerce "
    "sales, advertising performance, customer acquisition, "
    "and marketing efficiency across Shopify, Google Ads, "
    "and Meta Ads."
)

st.caption(
    "Built with Python, Streamlit, and Pandas | "
    "Portfolio demonstration using fictional data"
)

st.divider()
st.markdown("[Visit my portfolio](https://tomascorza.me)")
st.info('Demo data is entirely fictional. Uploaded CSV data is used in your running Streamlit session; do not deploy a public app for sensitive exports without appropriate security controls.')

with st.sidebar:
    st.header('Data source')
    mode=st.radio('Choose dataset',['Fictional sample data','Upload your CSV files'])
    if mode=='Upload your CSV files':
        sales_file=st.file_uploader('Sales CSV',type='csv')
        ads_file=st.file_uploader('Ads CSV',type='csv')
        st.caption('Upload both files using the example column schemas in the README.')
        if sales_file is None or ads_file is None:
            st.warning('Upload both files to continue.')
            st.stop()
        sales_raw=pd.read_csv(sales_file)
        ads_raw=pd.read_csv(ads_file)
    else:
        sales_raw=pd.read_csv(ROOT/'data/sample/shopify_sales.csv')
        ads_raw=pd.read_csv(ROOT/'data/sample/paid_ads.csv')
try:
    sales=normalize_sales(sales_raw)
    ads=normalize_ads(ads_raw)
except (ValueError,KeyError,TypeError) as exc:
    st.error(f'Input validation error: {exc}')
    st.stop()

all_dates=pd.concat([sales['date'],ads['date']]).dropna()
if all_dates.empty:
    st.warning('Your files have no rows to analyze.')
    st.stop()
start,end=all_dates.min().date(),all_dates.max().date()
with st.sidebar:
    st.header('Filters')
    interval=st.date_input('Date range',value=(start,end),min_value=start,max_value=end)
    if not isinstance(interval,(tuple,list)) or len(interval)!=2:
        st.info('Select both start and end dates.')
        st.stop()
    a,b=interval
    if a>b:
        st.error('Start date must be on or before end date.')
        st.stop()
    platforms=sorted(ads['platform'].unique().tolist())
    chosen=st.multiselect('Ad platforms',platforms,default=platforms)
    st.caption('Platform selection filters paid media only, not total store sales.')

sales=filter_dates(sales,a,b)
ads=filter_dates(ads,a,b)
ads=ads[ads['platform'].isin(chosen)].copy()
k=summarize(sales,ads)

def money(v): return f'${v:,.2f}' if v is not None else 'N/A'
def ratio(v): return f'{v:,.2f}×' if v is not None else 'N/A'

st.subheader('Store performance')
c=st.columns(4)
c[0].metric('Net sales (provided)',money(k['revenue']))
c[1].metric('Orders',f"{k['orders']:,}")
c[2].metric('Average order value',money(k['aov']))
c[3].metric('New customers',f"{k['new_customers']:,}")
st.subheader('Paid media overview')
c=st.columns(4)
c[0].metric('Ad spend',money(k['spend']))
c[1].metric('MER · sales / spend',ratio(k['mer']))
c[2].metric('Blended CAC · spend / store new customers',money(k['blended_cac']))
c[3].metric('Platform-reported ROAS',ratio(k['platform_roas']))
st.caption('Platform-attributed revenue can overlap across platforms or differ from Shopify sales. Do not add platform-attributed revenue to store sales. When no spend/customers are present, ratios display N/A.')

daily=daily_table(sales,ads)
t1,t2,t3=st.tabs(['Trends','Campaigns','Export'])
with t1:
    st.subheader('Daily sales and ad spend')
    if daily.empty: st.info('No data in the selected date range.')
    else:
        st.line_chart(daily.set_index('date')[['revenue','spend']],height=340)
        st.bar_chart(daily.set_index('date')[['orders','new_customers']],height=280)
with t2:
    table=campaign_table(ads)
    if table.empty: st.info('No ad campaigns match these filters.')
    else:
        st.dataframe(table,hide_index=True,use_container_width=True,column_config={
            'spend':st.column_config.NumberColumn('Spend',format='$%.2f'),
            'attributed_revenue':st.column_config.NumberColumn('Attributed revenue',format='$%.2f'),
            'roas':st.column_config.NumberColumn('ROAS',format='%.2fx'),
            'cac':st.column_config.NumberColumn('Attributed CAC',format='$%.2f'),
            'cpa':st.column_config.NumberColumn('Attributed CPA',format='$%.2f')})
        st.bar_chart(table.set_index('campaign')[['spend','attributed_revenue']])
with t3:
    st.subheader('Download filtered analysis')
    st.download_button('Download daily summary CSV',daily.to_csv(index=False).encode('utf-8'),file_name='daily_summary.csv',mime='text/csv')
    st.download_button('Download campaign summary CSV',campaign_table(ads).to_csv(index=False).encode('utf-8'),file_name='campaign_summary.csv',mime='text/csv')
    st.markdown('The source data remains unchanged. Calculations use the filtered date range and selected advertising platforms.')
