import json


def loadData():
    with open("variables.json") as json_data_file:
        data = json.load(json_data_file)
    return data

def updateData(dumpData):
    with open('variables.json', 'w') as json_data_file:
        json.dump(dumpData, json_data_file)