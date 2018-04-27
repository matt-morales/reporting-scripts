import requests
from pprint import pprint
import xlsxwriter
import datetime
import pandas as pd
import json

token = my_token

pd.options.display.float_format = '{:.0f}'.format
df_campaigns = pd.read_excel('/Users/mmorale5/desktop/currently_running_campaigns.xlsx', sheet_name='Campaigns', header=0)
print df_campaigns
df_fields = pd.read_excel('/Users/mmorale5/desktop/currently_running_campaigns.xlsx', sheet_name='Fields', header=0)
field_list = df_fields['Fields'].tolist()
action_list = df_fields['Actions'].tolist()[0:2]
fields = ",".join(field_list)
actions = ",".join(action_list)

today = datetime.date.today()
today_list = str(datetime.date.today()).split("-")
month_day = today_list[1] + today_list[2]

def request_fb_campaign(fb_id, f):
    url = "https://graph.facebook.com/v2.12/%s/insights?fields=%s&date_preset=lifetime&access_token=%s" % (int(fb_id), f, token)
    r = requests.get(url).json()
    return r

def fb_insights_stats(fb_id):
    r = request_fb_campaign(int(fb_id), fields)['data']
    df = pd.DataFrame.from_dict(r)
    return df

def fb_actions_stats(fb_id):
    r = request_fb_campaign(int(fb_id), actions)['data']
    if len(r) > 0 and 'actions' in r[0]:
        for a in r[0]['actions']:
            if a['action_type'] == 'offsite_conversion.fb_pixel_purchase':
                return int(a['value'])
    return 0

def fb_link_clicks(fb_id):
    r = request_fb_campaign(int(fb_id), actions)['data']
    if len(r) > 0 and 'actions' in r[0]:
        for a in r[0]['actions']:
            if a['action_type'] == 'link_click':
                return int(a['value'])
    return 0

def fb_rsvp(fb_id):
    r = request_fb_campaign(fb_id, actions)['data']
    if len(r) > 0 and 'actions' in r[0]:
        for a in r[0]['actions']:
            if a['action_type'] == 'rsvp':
                return int(a['value'])
    return 0

def fb_action_value_stats(fb_id):
    r = request_fb_campaign(int(fb_id), actions)['data']
    if len(r) > 0 and 'action_values' in r[0]:
        for a in r[0]['action_values']:
            if a['action_type'] == 'offsite_conversion.fb_pixel_purchase':
                return a['value']
    return 0

def get_campaign_stats(campaign_info_df):
    for index, row in campaign_info_df.iterrows():
        print index
        if index == 0:
            conversions = fb_actions_stats(row['FB Campaign Group ID'])
            revenue = fb_action_value_stats(row['FB Campaign Group ID'])
            link_clicks = fb_link_clicks(row['FB Campaign Group ID'])
            rsvp = fb_rsvp(row['FB Campaign Group ID'])
            df_main = fb_insights_stats(row['FB Campaign Group ID'])
            df_main['Start Date'] = row['Start Date']
            df_main['Stop Date'] = row['Stop Date']
            df_main['Group ID'] = row['Group ID']
            df_main['Group Name'] = row['Group Name']
            df_main['Campaign ID'] = row['Campaign ID']
            df_main['Flight'] = row['Flight']
            df_main['clicks'] = int(df_main['clicks'])
            df_main['impressions'] = int(df_main['impressions'])
            df_main['reach'] = int(df_main['reach'])
            df_main['spend'] = float(df_main['spend'])
            df_main['Link Clicks'] = int(link_clicks)
            df_main['Conversions'] = int(conversions)
            df_main['RSVPs'] = int(rsvp)
            df_main['Revenue'] = float(revenue)
            df_main['Est. Tickets Sold'] = 2.1*df_main['Conversions']
            df_main['CPC'] = df_main['spend']/df_main['clicks']
            df_main['CPLC'] = df_main['spend']/df_main['Link Clicks']
            df_main['CP RSVP'] = df_main['RSVPs']/df_main['Link Clicks']
            df_main['Est. CPT'] = df_main['spend']/df_main['Est. Tickets Sold']
            df_main['ROI'] = df_main['Revenue']/df_main['spend']
            df_main['Budget'] = float(row['Budget']/100)
        else:
            df_new = fb_insights_stats(row['FB Campaign Group ID'])
            if len(df_new) > 0:
                conversions = fb_actions_stats(row['FB Campaign Group ID'])
                revenue = fb_action_value_stats(row['FB Campaign Group ID'])
                link_clicks = fb_link_clicks(row['FB Campaign Group ID'])
                rsvp = fb_rsvp(row['FB Campaign Group ID'])
                df_new['Start Date'] = row['Start Date']
                df_new['Stop Date'] = row['Stop Date']
                df_new['Group ID'] = row['Group ID']
                df_new['Group Name'] = row['Group Name']
                df_new['Campaign ID'] = row['Campaign ID']
                df_new['Flight'] = row['Flight']
                df_new['clicks'] = int(df_new['clicks'])
                df_new['impressions'] = int(df_new['impressions'])
                df_new['reach'] = int(df_new['reach'])
                df_new['spend'] = float(df_new['spend'])
                df_new['Link Clicks'] = int(link_clicks)
                df_new['Conversions'] = int(conversions)
                df_new['RSVPs'] = int(rsvp)
                df_new['Revenue'] = float(revenue)
                df_new['Est. Tickets Sold'] = 2.1*df_new['Conversions']
                df_new['CPC'] = df_new['spend']/df_new['clicks']
                df_new['CPLC'] = df_new['spend']/df_new['Link Clicks']
                df_new['CP RSVP'] = df_new['RSVPs']/df_new['Link Clicks']
                df_new['Est. CPT'] = df_new['spend']/df_new['Est. Tickets Sold']
                df_new['ROI'] = df_new['Revenue']/df_new['spend']
                df_new['Budget'] = float(row['Budget']/100)
                df_main = pd.concat([df_main, df_new], ignore_index=True)
    return df_main

def run_report(campaign_info_df):
    sheetname = 'Current Campaigns'
    # filename = '/Users/mmorale5/desktop/Daily Campaign Reports/campaign_performance_%s.xlsx' % (month_day)
    filename = '/Users/mmorale5/desktop/Tour Recap %s.xlsx' % (month_day)
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    df = get_campaign_stats(campaign_info_df)
    df.to_excel(writer, sheet_name=sheetname)
    writer.save()

run_report(df_campaigns)

