import json
import requests
import pandas as pd

headers = {
	  'app-token': 'YOURTOKEN',
	  'Content-Type': 'application/x-www-form-urlencoded'
	}

def fetchAccounts():

	url = "https://api.totango.com/api/v1/search/accounts"
	query = 'YOURFILTER'
	


	total_hits=1000
	json_query = json.loads(query)
	_df_allaccounts = pd.DataFrame()
	while json_query['offset'] < total_hits:
		payload = 'query=' + json.dumps(json_query) + '&teams_id=-1'
		response = requests.request("POST", url, headers=headers, data=payload)
		resp = json.loads(response.text)
		json_query['offset']+=1000
		total_hits= resp['response']['accounts']['total_hits']
		jsonString=json.dumps(resp['response']['accounts']['hits'])
		_df = pd.read_json(jsonString)
		_df_allaccounts = _df_allaccounts.append(_df,ignore_index = True,sort = False)
	
	return(_df_allaccounts)


def fetchEvents(_df_accounts):

	_df_events = pd.DataFrame()
	
	for index,row in _df_accounts.iterrows():

		#try:

		print('working on ' , row['name'])
		accountID = row['name']
		url = "https://api.totango.com/api/v2/events?account_id=" + accountID
		response = requests.request("GET", url, headers=headers)
		resp = json.loads(response.text)
		jsonString=json.dumps(resp)
		_df = pd.read_json(jsonString)
		tempstring = {''}
		_df = _df[(_df['note_content']==_df['note_content'])]
		_df['accountID']=accountID
		_df_events = _df_events.append(_df,ignore_index = True,sort = False)
		# except:
		# 	print('----------')
		# 	print('something made me stop')
		# 	print('----------')
		# 	pass
	for index,row in _df_events.iterrows():
		tempstring = row['note_content']
		_df_events.at[index,'note_id'] = tempstring['note_id']
		_df_events.at[index,'event_id'] = row['id']
		_df_events.at[index,'content'] = tempstring['text']
		_df_events.at[index,'userid'] = tempstring['totango_user']['user_name']
		tempstring = row['properties']
		try:
			_df_events.at[index,'create_date'] = tempstring['creation_time']
		except:
			pass
		_df_events.at[index,'activity_type_id'] = tempstring['activity_type_id']
		try:
			_df_events.at[index,'subject'] = tempstring['subject']
		except:
			pass
		try:
			_df_events.at[index,'touchpointType'] = tempstring['meeting_type']
		except:
			pass

	return(_df_events)


df_retrievedEvents = fetchEvents(fetchAccounts().copy(deep=True)).copy(deep=True)
df_retrievedEvents.to_csv('events.csv')
