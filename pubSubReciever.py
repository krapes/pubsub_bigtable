"""
Based on blog: https://medium.com/faun/writing-a-pub-sub-stream-to-bigquery-401b44c86bf
"""

import json
import base64
import datetime

from google.cloud import bigtable
from google.cloud.bigtable import column_family
from google.cloud.bigtable import row_filters

project_id = 'empack-238417'
instance_id = 'iotincoming'
table_id = 'incomingraw'

client = bigtable.Client(project=project_id, admin=True)
instance = client.instance(instance_id)
table = instance.table(table_id)

def main(event, context):
	print("Printing Event")
	print(event)
	data = event['data']
	data = base64.b64decode(data).decode('utf-8')
	date, lat, longitud, a, b, c, d = data.split(',')
	print("DATA: {}".format(data))

	timestamp=datetime.datetime.utcnow()

	row_key = '{}'.format(timestamp).encode()
	row = table.row(row_key)
	row.set_cell('lat',
					'latitude',
					lat,
					timestamp=datetime.datetime.utcnow())
	row.set_cell('long',
					'longitud',
					longitud,
					timestamp=datetime.datetime.utcnow())
	print(row)
	table.mutate_rows([row])