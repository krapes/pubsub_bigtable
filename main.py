import os

import pubSubReciever_handler
import mock_sensorData_handler




def pubSubReciever_dev(event, context):
	return pubSubReciever_handler.main(event, context)
def pubSubReciever_test(event, context):
	return pubSubReciever_handler.main(event, context)
def pubSubReciever_prod(event, context):
	return pubSubReciever_handler.main(event, context)


def mock_sensorData_dev(event):
	return mock_sensorData_handler.main(event)
def mock_sensorData_test(event):
	return mock_sensorData_handler.main(event)
def mock_sensorData_prod(event):
	return mock_sensorData_handler.main(event)

