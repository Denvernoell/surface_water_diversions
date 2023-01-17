import arrow
import pandas as pd
import streamlit as st
import requests
import json
import numpy as np
from bs4 import BeautifulSoup

st.set_page_config(
	page_title="Aliso Surface Water Diversion Check",
	layout="wide",
	page_icon="https://www.waterboards.ca.gov/images/banner/web_menu_graphic_sb.png"
	)
st.title("Aliso Surface Water Diversion Check")


pd.options.display.float_format = '{:,.0f}'.format

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
	def __init__(self,station,sensors,dur_code,start_date=start_date,end_date=end_date):
		start = start_date.format('YYYY-MM-DD')
		end = end_date.format('YYYY-MM-DD')
		self.station = station
		self.sensors = sensors

		url = f'https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet?Stations={station}&SensorNums={sensors}&dur_code={dur_code}&Start={start}&End={end}'
		R = requests.get(url)
		J = json.loads(R.text)

		# This creates the dataframe and drops the last row
		# df = pd.DataFrame(J)[:-1]
		df = pd.DataFrame(J)

		if dur_code == "H":
			df = pd.DataFrame(J)[:-1]
			# ! excel export and json export are shifted by 1
			# df = df.shift(1, freq='H')
		elif dur_code == "D":
			# df = pd.DataFrame(J)[1:]
			df = pd.DataFrame(J)[:-1]

		df.index = pd.to_datetime(df['date'])
		df['value'] = df['value'].where(df['value']>-9990,np.nan)
		self.flow = df

	def display(self):		
		st.markdown(f"**{self.station}**")
		# Date station id, flow, units
		df = self.flow
		# df['value'] = df['value'].map('${:,.0f}'.format)
		# df['value'] = df['value'].astype(float).map('${:,.0f}'.format)

		st.dataframe(df[['value']].style.format("{:,.0f}"))
		if self.sensors == "20":
			st.markdown(f"**Rolling Average = {self.flow['value'].mean():,.0f}**")


def get_USGS_flow(site,start_date, end_date):
	"""
	takes start and end date as arrow
	local:    https://waterservices.usgs.gov/nwis/iv/?sites=11274000&parameterCd=00060&startDT=2023-01-13T10:51:58.023-08:00&endDT=2023-01-14T10:51:58.023-08:00&siteStatus=all&format=rdb
	st cloud: https://waterservices.usgs.gov/nwis/iv/?sites=11274000&parameterCd=00060&startDT=2023-01-13T18:51:31.183+00:00&endDT=2023-01-14T18:51:31.183+00:00&siteStatus=all&format=rdb
	"""
	
	# top fails on streamlit cloud because of time zone
	# time_format = "YYYY-MM-DDTHH:mm:ss.SSSZZ"
	time_format = "YYYY-MM-DDTHH:mm:ss.SSS-08:00"

	start_time = start_date.floor('day').format(time_format)
	end_time = end_date.floor('day').format(time_format)

	# Newman station
	url = f"https://waterservices.usgs.gov/nwis/iv/?sites={site}&parameterCd=00060&startDT={start_time}&endDT={end_time}&siteStatus=all&format=rdb"
	# st.markdown(url)
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

	# !Update this after April 1
	WY_index = df.loc[df['Forecast Date'] == 'Jan 1, 2023']['  75%'].iloc[0]
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









Checks, Operations, Conditions, Diagram = st.tabs(["Checks", "Operations", "Conditions","Diagram"])

with Checks:
	newman_percent_flow = get_90th_percentile_flow(
		start_date="1943-10-01",
		end_date="2022-06-05",
		percentile=90
		)
	newman_90 = newman_percent_flow.pipe(lambda df:df.loc[
		(df['month_nu'] == end_date.format('M'))
		& (df['day_nu'] == end_date.format('D'))
		])['p90_va'].astype(float).iloc[0]
	# Get newman and remove last row
	newman = get_USGS_flow(
		"11274000",
		start_date,
		end_date,
	)[:-1]


	newman['15012_00060'] = newman['15012_00060'].astype(float)
	newman.index = newman['datetime']
	newman_average = newman['15012_00060'].mean()
		

	DTO = CDEC_flow("DTO","23","D")
	ELN = CDEC_flow("ELN","20","H")

	CBP = CDEC_flow("CBP","20","H")

	GRF = CDEC_flow("GRF","20","H")
	SJB = CDEC_flow("SJB","20","H")

	CBP_flow = GRF.flow['value'] - SJB.flow['value']
	MIL_spill = CDEC_flow("MIL","71","D")
	MIL_regulated = CDEC_flow("MIL","85","D")



	show_condition(
		"period of 1/1/ 2023 to 6/14/2023",
		arrow.get('2023-01-01','YYYY-MM-DD') < end_date < arrow.get("2023-06-14","YYYY-MM-DD"),
		)
	# Uncomment this until April 1 comes out
	# show_condition(
	# 	"b. The water year type (April 1) is 'below normal', 'normal', or Wet based on bulletin 120",
	# 	get_water_year_classification()
	# )

	show_condition(
		"There must not be any curtailments of Post 1914 appropriators on the Chowchilla River",
		get_curtailment_status()
	)


	show_condition(
		"c. Newman Gage (11274000) instantaneous of mean flow for previous 24 hour period greater than the published daily 90th percentile for 1/1 through 3/31",
		newman_average > newman_90,	
		)

	show_condition("a. delta outflow is above 44,500 cfs",DTO.flow['value'].iloc[0] > 44500)

	show_condition(
		"b. ELN instantaneous of mean flow for pervious 24 hour period greater than or equal 1297 CFS.",
		ELN.flow['value'].mean() >= 1297
		)

	show_condition(
		"a. CBP instantaneous of mean flow for previous 24 hour period greater than or equal 1938 CFS.",
		# CBP.flow['value'].mean() >= 1938
		CBP_flow.mean() >= 1938
		)


with Operations:

	st.markdown("## Diversion Conditions")
	"No more than 10,000 AF in season"

	# "l. 20% calculation of daily flow at CBP gage for Jan 1 to March 31"
	# "a. Diversion does not exceed 20% of daily flow at CBP" 
	"Max flow rate is no more than the lower of 100 CFS or 20% of CBP flow"
	CBP_20 = CBP_flow.mean() * .20
	st.markdown(f"20% of CBP flow = {CBP_20:,.0f} CFS")
	max_diversion = min(100,CBP_20)

	st.metric("Max flow rate", f"{max_diversion:,.0f} CFS")



	# CBP_20 = CDEC_flow(
	# 		"CBP",
	# 		"20",
	# 		"H",
	# 		arrow.get('Jan 1,2023',"MMM D,YYYY").format('YYYY-MM-DD'),
	# 		arrow.get('Mar 31, 2023',"MMM D, YYYY").format('YYYY-MM-DD')).flow
	# # st.dataframe(flow)

	# st.markdown(flow['value'].mean() * 0.2)

	# st.markdown(CBP_flow.columns)

with Conditions:
	with st.expander("Delta Outflow"):
		DTO.display()
	with st.expander("e. Hourly and 24 hour rolling mean flow of Eastside Bypass at El Nido (Gage ELN)"):
		ELN.display()

	with st.expander("g. daily 90th percentile flow values published by USGS at Newman Gage (Jan1 -Mar 31)"):
		st.markdown(f"{newman_90:,.0f} CFS")


	with st.expander("c. Hourly and 24 hour rolling mean flow of SJR at Newman (Gage 11274000)"):
		st.dataframe(newman[["15012_00060"]].style.format("{:,.0f}"))
		st.markdown(f"Rolling Average = {newman_average:,.0f} CFS")



	with st.expander("d. Hourly and 24 hour rolling mean flow of Chowchilla Bypass Gaging Station (Gage CBP)"):
		CBP.display()

	with st.expander("CBP is down. Use GRF - SJR"):
		GRF.display()
		SJB.display()


	with st.expander("f. Daily record of spillway discharge and control regulating discharge from Friant (Gage MIL)"):
		MIL_spill.display()
		MIL_regulated.display()

with Diagram:
	# """
	# use graphviz to draw a diagram starting with flow at MIL going to GFR then SJB  then ELN then newman
	# """
	# https://graphviz.org/doc/info/shapes.html
	shape = "box"
	st.graphviz_chart(f"""
	digraph G {{
		rankdir=TB;
		MIL [label = "MIL regulated = {MIL_regulated.flow['value'].mean():,.0f}\nMIL spill = {MIL_spill.flow['value'].mean():,.0f}" shape=cylinder]
		CBP [label = "GRF = {GRF.flow['value'].mean():,.0f} CFS\n- SJB = {SJB.flow['value'].mean():,.0f} CFS\n---------------\nCBP = {CBP_flow.mean():,.0f} CFS" shape={shape}]
		ELN [label = "ELN = {ELN.flow['value'].mean():,.0f} CFS" shape={shape}]
		POD [label = "POD max diversion = {max_diversion:,.0f} CFS" shape=rpromoter]
		newman [label = "Newman = {newman_average:,.0f} CFS" shape={shape}]
		DTO [label = "DTO = {DTO.flow['value'].mean():,.0f} CFS" shape={shape} style=filled fillcolor=green]
		AWD [label = "Aliso Water District" shape=box3d]

		node [shape=box];

		MIL ->
		CBP ->	POD -> AWD
		CBP ->	ELN -> 

		newman ->
		DTO
		;
	}}
	""",use_container_width=True)

		# GRF [label = {}] ->
		# SJB [label = {SJB.flow['value'].mean()}] ->