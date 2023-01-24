import smtplib
from email.message import EmailMessage
from os.path import basename

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from email.mime.application import MIMEApplication

# import tomli
# # read config.toml as config
# with open('..\\.streamlit\\secrets.toml','rb') as f:
# 	config = tomli.load(f)
# config = st.secrets

def email_alert(to,cc,subject,body,files=None):
	username = st.secrets['username']
	password = st.secrets['password']
	msg = EmailMessage()
	msg.set_content(body)
	msg['Subject'] = subject
	msg['to'] = to
	if cc is not None:
		msg['Cc'] = cc
	msg['from'] = username
	if files:
		for file in files:
			with open(file, 'rb') as f:
				file_data = f.read()
			# msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file)
			msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file)

	# 		with open(f,'rb') as fil:
	# 			part = MIMEApplication(fil.read(),Name=basename(f))
	# 		part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
	# 		msg.attach(part)

	server = smtplib.SMTP("smtp-mail.outlook.com",587)
	server.starttls()
	server.login(username,password)

	server.send_message(msg)
	server.quit()

class License:
	def __init__(self,WR_id) -> None:
		self.id = WR_id
		self.get_curtailment_status()
		

	def get_curtailment_status(self):
		from tableauscraper import TableauScraper as TS
		url ='https://public.tableau.com/shared/Y7D4HBGG2'
		ts = TS()
		ts.loads(url)
		wb = ts.getWorkbook()
		df = wb.getCsvData('Curtailment List')
		# return df
		# if water_right_id:
		curtailments = df.pipe(lambda df: df.loc[df['WR ID'] == self.id])
		# if subwatershed:
		# 	curtailments = df.pipe(lambda df: df.loc[df['Subwatershed'] == subwatershed])
		self.curtailments = curtailments
		self.owner = self.curtailments['Primary Owner'].iloc[0]

		manual_c = curtailments.pipe(lambda df: [i for i in df['Currently Curtailed? (Manual Changes)'].unique()])
		automatic_c = curtailments.pipe(lambda df: [i for i in df['Currently Curtailed? (Automatic)'].unique()])
		if manual_c == automatic_c == ['Not Curtailed']:
			self.curtailment_status = "Not Curtailed"
		else:
			self.curtailment_status = "Curtailed"

	def send_confirmation(self):
		# print(self.owner)
		subject = f"{self.id} Curtailment Status"
		email_alert(
			# to=["sharper@ppeng.com"],
			to=["dnoell@ppeng.com"],
			# cc=["dnoell@ppeng.com"],
			cc=None,
			subject=subject,
			body=f"""
Sara,

The curtailment status of {self.id} for {self.owner} is {self.curtailment_status}.

Please let me know if you have any questions.

Denver
	""",
	# files=[projected_pdf_path,actual_pdf_path]
	)

import streamlit as st
st.title("Curtailment Status")
L = License("A013541")

st.markdown(f"Curtailment Status: {L.curtailment_status}")


def job():
	L.send_confirmation()

if st.button("Run"):
	job()

import schedule
schedule.every(1).minutes.do(job)
