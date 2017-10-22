import os
import sys
import glob
import json
import time
from os.path import expanduser
import xlsxwriter.styles
from collections import OrderedDict


config_file_path = sys.argv[1]
results_path = sys.argv[2]


with open(config_file_path) as conf_file:
    conf_data = json.load(conf_file)

results_directory = results_path
# results_directory = conf_data['resultsDirectory']
print('***********************')
print(results_path)
files_list = glob.glob(expanduser('%s/*.json' % results_directory))

number_of_parties = list(conf_data['numOfParties'].values())

parties = set()
for file in files_list:
    parties.add(int(file.split('_')[5].split('.')[0].split('=')[1]))

results_headers = set()
for file in files_list:
    results_headers.add(file.split('_')[3])

parties = list(parties)
results_headers = list(results_headers)

parties_files_list = list()
headers_files_list = list()


# split files according to their task name
for party in parties:
    for header in results_headers:
        files_headers = list()
        for file in files_list:
            if header in file and 'numberOfParties=%s' % str(party) in file:
                files_headers.append(file)
        headers_files_list.append(files_headers)


results_directory = conf_data['resultsDirectory']
protocol_name = conf_data['protocol']

protocol_time = str(time.time())
wb = xlsxwriter.Workbook('Results/Results_%s_%s.xlsx' % (protocol_name, protocol_time))
style1 = wb.add_format({'num_format': '#.##'})

ws = wb.add_worksheet(protocol_name)
ws.write(0, 0, 'Phase/Number of Parties')

counter = 0
for party_idx in range(len(parties)):
    ws.write(0, party_idx + 1, parties[party_idx])
    for header_idx in range(len(results_headers)):
        header_data = 0
        ws.write(header_idx + 1, 0, results_headers[header_idx])
        for data_file in headers_files_list[header_idx + len(results_headers) * party_idx]:
            with open(data_file, 'r') as f:
                data = json.load(f)
            header_data += int(data[results_headers[header_idx]]['duration'])
        counter += 1
        ws.write(header_idx + 1, party_idx + 1, header_data // len(headers_files_list[header_idx + 2 * party_idx]))


wb.close()

os.system('git add Results/Results_%s_%s.xlsx' % (protocol_name, protocol_time))
os.system('git commit -m \"Add results file for Experiment: %s\"' % protocol_name)
os.system('git push https://liorbiu:4aRotdy0vOhfvVgaUaSk@github.com/cryptobiu/MATRIX')

