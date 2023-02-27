import pandas as pd
from playwright.sync_api import Playwright, sync_playwright, expect

class Session:
	def __init__(self,playwright: Playwright,config):
		browser = playwright.chromium.launch(
			headless=False,
			# slow_mo=0
			)
		context = browser.new_context()
		self.page = context.new_page()
		self.page.goto(config['url'])

		folder_path = r'\\ppeng.com\pzdata\clients\Aliso WD-2500\Ongoing\300 Surface Water\303_Temporary Water Diversion'
		file_path = f"{folder_path}\\new_flood.pdf"
		self.page.pdf(path=file_path)

		# self.page.

	# 	self.page.get_by_label("Login").fill(config['username'])
	# 	self.page.locator("#Password").fill(config['password'])
	# 	self.page.get_by_role("button", name="Log in").click()

	# 	# TODO figure out how to do this if it is there
	# 	# page.get_by_role("textbox", name="Required in case we need to contact you.").fill("sharper@ppeng.com")
	# 	# page.get_by_role("button", name="Continue").click()
		
	# 	self.page.get_by_role("row", name="Request For Additional Time Survey Summary").get_by_role("link", name="Survey").click()
	# 	self.page.get_by_role("button", name="Next").click()

	# 	if config["client"] == "Rio Vista":
	# 		self.rio_vista()
	# 	elif config["client"] == "Tivy":
	# 		self.tivy()
	# 	elif config["client"] == "San Bernardo":
	# 		self.san_bernardo()

	# 	file_path = f"{config['folder_path']}\\Submitted Request for Additional Time_{config['username']}_02032023_request.pdf"
	# 	self.page.emulate_media(media="screen")
		
	# def rio_vista(self) -> None:
	# 	self.page.get_by_label("Additional time needed to deal with unforeseen circumstances").check()
	# 	self.page.get_by_role("button", name="Next").click()
	# 	self.page.locator("#q2192").select_option("12")
	# 	self.page.locator("#q2193").click()
	# 	self.page.locator("#q2193").fill("Rio Vista Vineyard, LLC recently acquired this property and is in the process of doing its due diligence to ensure that they are reporting accurately and in accordance with the SWRCB guidance/\nregulations (SB88).")
	# 	self.page.locator("#q2194").click()
	# 	self.page.locator("#q2194").fill("Rio Vista Vineyard, LLC will continue to measure and monitor diversions with the equipment currently installed and at its earliest convenience modify existing equipment/install additional\nequipment to measure and record diversions at the frequency required pursuant to SB 88")
	# 	self.page.get_by_role("button", name="Next").click()
	# 	self.page.get_by_role("button", name="Next").click()
	# 	self.page.get_by_label("I hereby certify that the above information is true and correct to the best of my knowledge and belief.     *").check()
	# 	self.page.get_by_label("Agent").check()
	# 	self.page.locator("#q2199").click()
	# 	self.page.locator("#q2199").fill("Sara Harper")
	# 	self.page.get_by_role("button", name="Finish and Submit").click()

	# def san_bernardo(self):
	# 	self.page.get_by_label("Additional time needed to deal with unforeseen circumstances").check()
	# 	self.page.get_by_role("button", name="Next").click()
	# 	self.page.locator("#q2192").select_option("24")
	# 	self.page.locator("#q2193").click()
	# 	self.page.locator("#q2193").click()
	# 	self.page.locator("#q2193").fill("The water right holder is currently evaluating measurement and reporting requirements at each point of diversion to develop a reporting protocol in compliance with SB88. Recent flooding in and near the place of use for the water rights listed in this form have caused undue hardship on the water right holder and they are in the process of coordinating with local/state/federal agencies to mitigate damage. It is unclear at this time if/what extent of damage has occurred to the measurement devices currently installed and measuring diversions.")
	# 	self.page.locator("html").click()
	# 	self.page.locator("#q2194").click()
	# 	self.page.locator("#q2194").fill("The water right holder/lessee's on the property will continue to measure and monitor diversions with the equipment currently installed and at its earliest convenience modify existing equipment/ install additional equipment to measure and record diversions at the frequency required pursuant to SB 88")
	# 	self.page.get_by_role("button", name="Next").click()
	# 	self.page.get_by_role("button", name="Next").click()
	# 	self.page.get_by_label("I hereby certify that the above information is true and correct to the best of my knowledge and belief.     *").check()
	# 	self.page.get_by_label("Designated Contact").check()
	# 	self.page.locator("#q2199").click()
	# 	self.page.locator("#q2199").fill("Sara Harper")
	# 	self.page.get_by_role("button", name="Finish and Submit").click()

	# def tivy(self):
	# 	self.page.get_by_label("Additional time needed to deal with unforeseen circumstances").check()
	# 	self.page.get_by_role("button", name="Next").click()
	# 	self.page.locator("#q2192").select_option("12")
	# 	self.page.locator("#q2193").click()
	# 	self.page.locator("#q2193").fill("Bifro Land Co. recently acquired this property and is in the process of doing its due diligence to ensure that they are reporting accurately and in accordance with the SWRCB guidance/regulations (SB88).")
	# 	self.page.locator("#q2194").click()
	# 	self.page.locator("#q2194").fill("Bifro Land Co. will continue to measure and monitor diversions with the equipment currently installed and at its earliest convenience modify existing equipment/install additional equipment to measure and record diversions at the frequency required pursuant to SB 88")
	# 	self.page.get_by_role("button", name="Next").click()
	# 	self.page.get_by_role("button", name="Next").click()
	# 	self.page.get_by_label("I hereby certify that the above information is true and correct to the best of my knowledge and belief.     *").check()
	# 	self.page.get_by_label("Designated Contact").check()
	# 	self.page.locator("#q2199").click()
	# 	self.page.locator("#q2199").fill("Cortland Barns")
	# 	self.page.get_by_role("button", name="Finish and Submit").click()

# file_path = r'\\services\u\harper\SWRCB\Water Rights\Water Right Client Summary.xlsx'
# df = pd.read_excel(
# 	file_path,
# 	sheet_name='Summary Table',
# 	skiprows=4,
# 	)

# clients = 	{
# 	"Rio Vista":r'\\ppeng.com\pzdata\clients\Baker Manock_Jensen-1033\103322005-Rio Vista Water Right_On Call Eng Srvcs\200 Technical\202 General\Request for Additional Time_SB88',
# 	"Tivy":r'\\ppeng.com\pzdata\clients\Baker Manock_Jensen-1033\103322011-Tivy Ranch Water Right Rpt Srvcs\200 Technical\202 General\Water Rights\Request for Additional Time_SB88',
# 	"San Bernardo":r'\\ppeng.com\pzdata\clients\San Bernardo Rancho- 3841\200 Technical\202 General\Water Rights\Request for Additional Time'
# }
# for client,folder_path in clients.items():
# 	data = df.loc[df['Request for Additional Time Format'] == client][['Username','SWRCB Annual Reporting eWRIMS RMS Passwords']]
# 	for i,y in data.iterrows():
# 		try:
# 			username = y['Username'].strip()
# 			password = y['SWRCB Annual Reporting eWRIMS RMS Passwords'].strip()
# 			print(f"Starting {username}. Password: {password}")
			
with sync_playwright() as playwright:
		
	config = {
		# "username":username,
		# "password":password,
		# "client":client,
		# "folder_path":folder_path,
		'url':'https://web.archive.org/web/20211229120842/http://cdec.water.ca.gov/reportapp/javareports?name=floodcontrol.pdf'
		}
	S = Session(playwright,config)