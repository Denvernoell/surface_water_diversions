import arrow
import pandas as pd
import streamlit as st
import requests
import json
import numpy as np
from bs4 import BeautifulSoup

st.title("Surface Water Diversion Check")
# date = st.date_input("Date")
# start_date = arrow.get(date)
start_date = arrow.now().shift(days=-2)
end_date = start_date.shift(days=1)

# st.markdown(f"**{start_date.format('YYYY-MM-DD')} - {end_date.format('YYYY-MM-DD')}**")
st.markdown(f"## {end_date.format('YYYY-MM-DD')}")

def show_condition(condition, passes):
	c1,c2 = st.columns(2)
	with c1:
		st.markdown(condition)
	with c2:
		if passes:
			st.success("Pass")
		else:
			st.error("Fail")

class CDEC_flow:
	def __init__(self,station,sensors,dur_code,start,end):

		url = f'https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet?Stations={station}&SensorNums={sensors}&dur_code={dur_code}&Start={start}&End={end}'
		R = requests.get(url)
		J = json.loads(R.text)

		# This creates the dataframe and drops the last row
		self.flow = pd.DataFrame(J)[:-1]
		if dur_code == "H":
			self.flow = self.clean_hourly()
		elif dur_code == "D":
			self.flow = self.clean_daily()


	def clean_daily(self):
		df = self.flow
		df.index = pd.to_datetime(df['date'])
		df['value'] = df['value'].where(df['value']>-9990,np.nan)
		return df

	def clean_hourly(self):
		df = self.flow
		df.index = pd.to_datetime(df['date'])
		# ! excel export and json export are shifted by 1
		df = df.shift(1, freq='H')
		df['value'] = df['value'].where(df['value']>-9990,np.nan)
		return df



def display_cdec(station,sensors,dur_code):
	st.markdown(f"**{station}**")
	flow = CDEC_flow(
		station,
		sensors,
		dur_code,
		start_date.format('YYYY-MM-DD'),
		end_date.format('YYYY-MM-DD')).flow

	st.dataframe(flow)
	if sensors == "20":
		st.markdown(f"**Rolling Average = {flow['value'].mean():.2f}**")
	return flow








def get_USGS_flow(site,start_time, end_time):
	# Newman station
	url = f"https://waterservices.usgs.gov/nwis/iv/?sites={site}&parameterCd=00060&startDT={start_time}&endDT={end_time}&siteStatus=all&format=rdb"
	st.markdown(url)
	df = pd.read_csv(url, skiprows=26, sep="\t")
	df = df.drop(index = [0])
	return df

def get_90th_percentile_flow(start_date, end_date, percentile=90):
	url = f"https://waterdata.usgs.gov/nwis/dvstat?&site_no=11274000&agency_cd=USGS&por_11274000_9587=2208812,00060,9587,{start_date},{end_date}&stat_cds=p{percentile}_va&referred_module=sw&format=rdb"
	df = pd.read_csv(url, skiprows=44, sep="\t")
	df = df.drop(index = [0])
	return df

def get_water_year_classification():
	url = "https://cdec.water.ca.gov/reportapp/javareports?name=WSI"
	R = requests.get(url)
	soup = BeautifulSoup(R.text,'html.parser')
	pres = soup.find_all('pre')

	T = pres[0]
	brs = T.string.split('\r\n\r\n')
	table_text =brs[11]
	table = BeautifulSoup(table_text,features="lxml").find_all('p')[0]
	rows = [i.split('   ') for i in table.text.split('\r\n')[2:]]
	df = pd.DataFrame(rows)
	df = df.iloc[:,[0,2,4,6,8,10,12]]
	df.columns = df.iloc[0]
	df = df.iloc[[2,3]]

	WY_index = df.loc[df['Forecast Date'] == 'Jan 1, 2023']['  90%'].iloc[0]
	if float(WY_index) > 2.5:
		return True
	else:
		return False



def get_curtailment_status():
	from tableauscraper import TableauScraper as TS
	url ='https://public.tableau.com/shared/Y7D4HBGG2'
	ts = TS()
	ts.loads(url)
	wb = ts.getWorkbook()
	df = wb.getCsvData('Curtailment List')
	curtailment_chowchilla = df.pipe(lambda df: df.loc[df['Subwatershed'] == 'Chowchilla'])
	manual_c = curtailment_chowchilla.pipe(lambda df: [i for i in df['Currently Curtailed? (Manual Changes)'].unique()])
	automatic_c = curtailment_chowchilla.pipe(lambda df: [i for i in df['Currently Curtailed? (Automatic)'].unique()])
	return manual_c == automatic_c == ['Not Curtailed']



show_condition(
	"period of 1/1/ 2023 to 6/14/2023",
	arrow.get('2023-01-01','YYYY-MM-DD') < end_date < arrow.get("2023-06-14","YYYY-MM-DD"),
	)

show_condition(
	"b. The water year type is 'below normal', 'normal', or Wet based on bulletin 120",
	get_water_year_classification()
)

show_condition(
	"There must not be any curtailments of Post 1914 appropriators on the Chowchilla River",
	get_curtailment_status()
)

try:
	percent_flow = get_90th_percentile_flow(
		start_date="1912-05-01",
		end_date="2022-06-05",
		percentile=90
		)

	date = end_date
	newman_90 = percent_flow.pipe(lambda df:df.loc[
		(df['month_nu'] == date.format('M'))
		& (df['day_nu'] == date.format('D'))
		])['p90_va'].astype(float).iloc[0]
	with st.expander("g. daily 90th percentile flow values published by USGS at Newman Gage (Jan1 -Mar 31)"):
		st.markdown(newman_90)

except Exception as e:
	st.write(e)

try:
	newman = get_USGS_flow(
		"11274000",
		start_date.format("YYYY-MM-DDTHH:mm:ss.SSSZZ"),
		end_date.format("YYYY-MM-DDTHH:mm:ss.SSSZZ"),
	)
	newman_average = newman['15012_00060'].astype(float).mean()
	with st.expander("c. Hourly and 24 hour rolling mean flow of SJR at Newman (Gage 11274000)"):
		st.dataframe(newman)
		st.markdown(f"**Rolling Average = {newman['15012_00060'].mean():.2f}**")
except Exception as e:
	st.write(e)

	# show_condition(
	# 	"c. Newman Gage (11274000) instantaneous of mean flow for previous 24 hour period greater than the published daily 90th percentile for 1/1 through 3/31",
	# 	newman_average > newman_90,	
	# 	)


# st.markdown("## Delta Outflow (DTO)")
flow = display_cdec("DTO","23","D")
show_condition("a. delta outflow is above 44,500 cfs",flow['value'].iloc[0] > 44500)


with st.expander("e. Hourly and 24 hour rolling mean flow of Eastside Bypass at El Nido (Gage ELN)"):
	ELN = display_cdec("ELN","20","H")

show_condition(
	"b. ELN instantaneous of mean flow for pervious 24 hour period greater than or equal 1297 CFS.",
	ELN['value'].mean() >= 1297
	)

"only divert when Delta in excess conditions (must check CVP SWP Ops)"




with st.expander("d. Hourly and 24 hour rolling mean flow of Chowchilla Bypass Gaging Station (Gage CBP)"):
	CBP = display_cdec("CBP","20","H")

show_condition(
	"a. CBP instantaneous of mean flow for previous 24 hour period greater than or equal 1938 CFS.",
	CBP['value'].mean() >= 1938
	)

with st.expander("f. Daily record of spillway discharge and control regulating discharge from Friant (Gage MIL)"):
	display_cdec("MIL","71","D")
	display_cdec("MIL","85","D")

st.markdown("## Diversion Conditions")

"no more than 100 CFS"
"no more than 10,000 AF"


"l. 20% calculation of daily flow at CBP gage for Jan 1 to March 31"
flow = CDEC_flow(
		"CBP",
		"20",
		"H",
		arrow.get('Jan 1,2023',"MMM D,YYYY").format('YYYY-MM-DD'),
		arrow.get('Mar 31, 2023',"MMM D, YYYY").format('YYYY-MM-DD')).flow
# st.dataframe(flow)
st.markdown(flow['value'].mean() * 0.2)

"a. Diversion does not exceed 20% of daily flow at CBP" 
st.markdown(f"Allowed diversion = {CBP['value'].mean() * .20}")



"only divert if Friant Dam is spilling uncrotrolled excess flows, or water is being relased ffrom Firant for Flood Control Purposes  (will need to look for press release or that conservation pool is encroached) "

"a. delta outflow is above 44,500 cfs"
