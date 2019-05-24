import pandas as pd
from datetime import datetime
import os
#============================================
#Program configuration
#============================================
#
DEBUGmode = 1 # Verbose 
DEBUGmode = 0 # Quiet
PATH = 'C:\\Work\\20190506_JET'
SCOPE_SH = 'SH_'
SCOPE_BJ = 'BJ_'
RESULT = 'JET'
BUSINESSLINE = 'GVAT_PBL_OU.xlsx'
ACCOUNTMAPPING = 'GVAT_BF10_4_GFS10.xlsx'
OUTFILEraw0 = "Raw0_data.csv"
OUTFILEraw1 = "Raw1_data.csv"
OUTFILEraw2 = "Raw2_data.csv"
OUTFILE1 = "JET_d_"
OUTFILE2 = "JET_e_"
OUTFILE3 = "JET__"
PROCDATE = " "
DocSN = 0
Jet_index = ['BusinessU','OperatingU','Account','Product','ProductSub','BookCode','Affliate',\
	'ProjectID','Class','Currency','Amount','ADBdate','Acctdate','TradeRef','Narrative',\
	'OperatingUA','AcctCode','RelationID','Reversal','IntraDay','Source', 'Trade Group ID', 'Client Code', 'Client Name', 'Doc Seq Number']
Jet_index_New = ['Business Unit','Operating Unit','Account','Product','Sub-Product','Book Code',\
	'Affliate','Project ID','Class','Currency','Amount','ADB Date','Accounting Date','Trade Ref', \
	'Narrative','Operating Unit Affliate','Acctg Reason Code','Relation ID','Reversal','IntraDay',\
	'Source', ' Trade Group ID', 'Client Code', 'Client Name', 'Doc Seq Number']
#
#============================================
#Reading mapping tables
#============================================
#
try:
	f = open(ACCOUNTMAPPING, "r")
	print("Reading Account Mapping file : " + ACCOUNTMAPPING)
except:
	print("Error Reading Account Mapping file : " + ACCOUNTMAPPING)
	exit()
AccMap = pd.read_excel(ACCOUNTMAPPING, index_col=None)
AccMap.columns = ['Account','ACOD','AccountPS','Product']
if DEBUGmode ==1:
	print(AccMap.head(10))

#============================================
#Reading Business line mapping tables
#============================================
#
try:
	f = open(BUSINESSLINE, "r")
	print("Reading Business Line file : "+BUSINESSLINE)
except:
	print("Error eeading Business Line file : "+BUSINESSLINE)
	exit()
RelationMap = pd.read_excel(BUSINESSLINE, sheet_name='PBL',index_col=None)
OUMap       = pd.read_excel(BUSINESSLINE, sheet_name='OU',index_col=None)

ROU = pd.merge(RelationMap, OUMap, how='left', on=['PBL'])

#============================================
#Constructing JET dataframe
#============================================
#
Jetdf = pd.DataFrame(columns = Jet_index)

#print(RelationMap.head(10))
#print(OUMap.head(10))

File_List = []

for r, d, f in os.walk(PATH):
	for file in f:
		if SCOPE_SH in file:
			File_List.append(os.path.join(r, file))
		elif SCOPE_BJ in file:
			File_List.append(os.path.join(r, file))

for FILE in File_List:
# Setup of all variables
	try:
		f = open(FILE, "r")
		print("Reading file : "+FILE)
	except:
		print("************************")
		print("Source files not aviable")
		print("************************")
		print("Program ABORTED!")
		print("************************")
		exit()

# Remove first header line
	header = f.readline()

	for body in f:
		TransType = body[243:244]
	#CDtype
		CDtype = body[242:243]
	#Amount
		Amount = float(body[228:242])
		if CDtype == "C":
			Amount = Amount * -1
	#
		RelationID =body[200:206]
		Currency =	body[210:213]
		Account  =  body[213:223]
		Seq       = body[223:225]
		BusinessU = body[225:228]
		OperatingU = "   "
		Product = "   "
		ProductSub = "   "
		BookCode = "B"
		Affliate = "   "
		ProjectID = "   "
		Class = "   "
		OperatingUA = "   "
		AcctCode = "GL"
		Reversal = "   "
		IntraDay = "N"
		Source = "MID"
		TradeGID = " "
		ClientCode = " "
		ClientName = " "
		DocSN = DocSN+1
		
		Jet = []
		Jet.append(BusinessU)
		Jet.append(OperatingU)
		Jet.append(Account)
		Jet.append(Product)
		Jet.append(ProductSub)
		Jet.append(BookCode)
		Jet.append(Affliate)
		Jet.append(ProjectID)
		Jet.append(Class)
		Jet.append(Currency)
		Jet.append(Amount)

		if TransType == "G":
			TradeRef = body[243:256]
			TradeRef = "  "
			Narrative = body[243:270]
			Cdate = body[257:265]
		elif TransType == "J":
			TradeRef = body[243:250]
			TradeRef = "  "
			Narrative = body[243:260]
			Cdate = body[251:259]
		elif TransType == "P":
			TradeRef = body[243:258]
			TradeRef = "  "
			Narrative = body[243:274]
			Cdate = body[259:267]
		else:
			TradeRef = "MCH"+body[243:251]
			Narrative = body[243:267]
			Cdate = body[252:260]

		PROCDATE = str(Cdate)
		Cdate = datetime.strptime(str(Cdate),'%Y%m%d')
		ADBdate = Cdate.strftime('%m/%d/%Y')
		Acctdate = ADBdate
		Jet.append(ADBdate)
		Jet.append(Acctdate)
		Jet.append(TradeRef)
		Jet.append(Narrative.strip())
		Jet.append(OperatingUA)
		Jet.append(AcctCode)
		Jet.append(RelationID)
		Jet.append(Reversal)
		Jet.append(IntraDay)
		Jet.append(Source)
		Jet.append(TradeGID)
		Jet.append(ClientCode)
		Jet.append(ClientName)
		Jet.append(DocSN)
#	Building a row
		Jet_Series=pd.Series(data=Jet,index=Jet_index)
	#	print(Jet_Series)
		Jetdf = Jetdf.append(Jet_Series, ignore_index=True)
	#print(Jetdf.head(15))
	#print(Jetdf.tail(15))

Jetdf.loc[Jetdf['BusinessU'] == "501", 'BusinessU'] = "CN001"
Jetdf.loc[Jetdf['BusinessU'] == "502", 'BusinessU'] = "CN002"
Jetdf.loc[Jetdf['BusinessU'] == "503", 'BusinessU'] = "CN003"
Jetdf.loc[Jetdf['Currency']  == "CNY", 'Currency']  = "RMB"

Jetdf.Account = Jetdf.Account.astype(str)
Jetdf.RelationID = Jetdf.RelationID.astype(str)
AccMap.Account = AccMap.Account.astype(str)
ROU.RelationID = ROU.RelationID.astype(str)

if DEBUGmode == 1:
	print(Jetdf.Account.head(15))
	print(Jetdf.dtypes)
	print(AccMap.dtypes)
	print(Jetdf.tail(15))

if DEBUGmode == 1:
	try:	
		Jetdf.to_csv(OUTFILEraw0,index=False)
		print("Generating raw data output file: " + OUTFILEraw0)
	except:
		print("Error generating raw output file: " + OUTFILEraw0)

Result = pd.merge(Jetdf, AccMap, how='left', on=['Account'])
if DEBUGmode == 1:
	try:	
		Result.to_csv(OUTFILEraw1,index=False)
		print("Generating raw data output file: " + OUTFILEraw1)
	except:
		print("Error generating raw output file: " + OUTFILEraw1)

Final = pd.merge(Result, ROU, how='left', on=['RelationID','BusinessU'])
if DEBUGmode == 1:
	try:	
		Final.to_csv(OUTFILEraw2,index=False)
		print("Generating raw data output file: " + OUTFILEraw2)
	except:
		print("Error generating raw output file: " + OUTFILEraw2)

if DEBUGmode == 1:
	print(Final.head(10))
	print(Final.tail(10))

for i in Final.index:
	Final.at[i, 'OperatingU'] = Final.at[i, 'OU']
	Final.at[i, 'Product_x'] = Final.at[i, 'Product_y']
	Final.at[i, 'Account'] = Final.at[i, 'AccountPS']
	if "MCHLE" in Final.at[i, 'TradeRef']:
		Final.at[i, 'RelationID'] = "  "
	else:
		Final.at[i, 'RelationID'] = "MCH"+ Final.at[i, 'RelationID']
			
#	Final.at[i, 'ACOD'] = int(Final.at[i, 'ACOD'])

Final = Final.drop(columns=['ACOD','Product_y','AccountPS','PBL','OU'])
Final.columns=Jet_index_New
if DEBUGmode ==1:
	try:
		OUTFILE1 = OUTFILE1 + PROCDATE + ".csv"
		Final.to_csv(OUTFILE1,index=False)
		print("Generating output file: " + OUTFILE1)
	except:
		print("Erro generating output file: " + OUTFILE1)

Conversion = Final.copy()
for i in Conversion.index:
	Conversion.at[i, 'Operating Unit'] = 'GT700000'
	Conversion.at[i, 'Account'] = '2670150000'
	Conversion.at[i, 'Product'] = 'I00011'
	Conversion.at[i, 'Amount'] = Conversion.at[i, 'Amount']  * -1

Combine = pd.concat([Final,Conversion])
try:
	OUTFILE3 = OUTFILE3 + PROCDATE + ".csv"
	Combine.to_csv(OUTFILE3,index=False)
	print("Generating output file: " + OUTFILE3)
except:
	print("Error Generating output file: " + OUTFILE3)