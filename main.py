import os

import pubSubReciever_handler
import simulate_accesoData




def pubSubReciever_dev(event, context):
	return pubSubReciever_handler.main(event, context)
def pubSubReciever_test(event, context):
	return pubSubReciever_handler.main(event, context)
def pubSubReciever_prod(event, context):
	return pubSubReciever_handler.main(event, context)


def simulateAccesoData_dev(event):
	return simulate_accesoData.main(event)
def simulateAccesoData_test(event):
	return simulate_accesoData.main(event)
def simulateAccesoData_prod(event):
	return simulate_accesoData.main(event)

