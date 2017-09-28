import glob
import json
from os.path import expanduser
import xlsxwriter.styles
from collections import OrderedDict


with open('config.json') as conf_file:
    conf_data = json.load(conf_file)

results_directory = conf_data['resultsDirectory']
files_list = glob.glob(expanduser('%s/*.json' % results_directory))

results_headers = set()
for file in files_list:
    results_headers.add(file.split('_')[2])

results_headers = list(results_headers)

files_headers_list = list()

# split files according to their task name
for header in results_headers:
    files_headers = list()
    for file in files_list:
        if header in file:
            files_headers.append(file)
    files_headers_list.append(files_headers)

print(files_headers_list)

with open(files_list[0]) as data_file:
    data = json.load(data_file, object_pairs_hook=OrderedDict)


min_num_of_parties = conf_data['minNumOfParties']
max_num_of_parties = conf_data['maxNumOfParties']
quanta = conf_data['partiesQuanta']
results_directory = conf_data['resultsDirectory']
protocol_name = conf_data['protocol']

wb = xlsxwriter.Workbook('Results.xlsx')
style1 = wb.add_format({'num_format': '#.##'})

ws = wb.add_worksheet(protocol_name)
ws.write(0, 0, 'Phase/Number of Parties')


for header_idx in range(len(results_headers)):
    ws.write(header_idx + 1, 0, results_headers[header_idx])
    header_data = 0
    for data_file in files_headers_list[header_idx]:
        with open(data_file, 'r') as f:
            data = json.load(f)
        header_data += int(data[results_headers[header_idx]]['duration'])
    ws.write(header_idx + 1, 1, header_data // len(files_headers_list[header_idx]))

wb.close()
