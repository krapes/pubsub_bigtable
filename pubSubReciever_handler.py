"""
Based on blog: https://medium.com/faun/writing-a-pub-sub-stream-to-bigquery-401b44c86bf
"""

import json
import base64
import os
from datetime import datetime

from google.cloud import bigtable
from google.cloud.bigtable import column_family, row_filters


project_id = os.environ.get('GCP_PROJECT', 'UNKNOWN')
INSTANCE = 'iotincoming'
TABLE = 'incomingraw_'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
STANDIN_SYSMAX = 10**20

client = bigtable.Client(project=project_id, admin=True)
instance = client.instance(INSTANCE)


def reverseTimestamp(ts):
	reverseTS = datetime.strptime(ts, TIME_FORMAT)
	reverseTS = datetime.strftime(reverseTS, '%Y%m%d%H%M%S%f')
	reverseTS = STANDIN_SYSMAX - int(reverseTS)
	return str(reverseTS)

def writeToBigTable(table, data):

	timestamp = data['event']['date']
	rts = reverseTimestamp(timestamp)
	row_key = '{}'.format(rts).encode()
	row = table.row(row_key)
	for colFamily in data.keys():
		for key in data[colFamily].keys():
			row.set_cell(colFamily,
									key,
									data[colFamily][key])

	table.mutate_rows([row])
	return data

def selectTable():
	stage = os.environ.get('stage', 'dev')
	table_id = TABLE + stage
	table = instance.table(table_id)
	return table


def main(event, context):

	data = base64.b64decode(event['data']).decode('utf-8')
	print("DATA: {}".format(data))
	date, lat, longitud, a, b, c, d = data.split(',')


	table = selectTable()

	data = {'event': {'date': date,
					  'latitude': lat,
					  'longitud': longitud}
			}

	writeToBigTable(table, data)
	print("Data Written: {}".format(data))