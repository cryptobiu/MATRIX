import glob
import json
from os.path import expanduser
import xlsxwriter.styles
from collections import OrderedDict


with open('config.json') as conf_file:
    conf_data = json.load(conf_file)

results_directory = conf_data['resultsDirectory']
files_list = glob.glob(expanduser('%s/*.json' % results_directory))
number_of_parties = list(conf_data['numOfParties'].values())

parties = set()
for file in files_list:
    parties.add(int(file.split('_')[4].split('.')[0].split('=')[1]))

results_headers = set()
for file in files_list:
    results_headers.add(file.split('_')[2])

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

print(headers_files_list)

with open(files_list[0]) as data_file:
    data = json.load(data_file, object_pairs_hook=OrderedDict)


results_directory = conf_data['resultsDirectory']
protocol_name = conf_data['protocol']

wb = xlsxwriter.Workbook('Results.xlsx')
style1 = wb.add_format({'num_format': '#.##'})

ws = wb.add_worksheet(protocol_name)
ws.write(0, 0, 'Phase/Number of Parties')

counter = 0
for party_idx in range(len(parties)):
    ws.write(0, party_idx + 1, parties[party_idx])
    for header_idx in range(len(results_headers)):
        header_data = 0
        print(header_idx + 2 * party_idx)
        ws.write(header_idx + 1, 0, results_headers[header_idx])
        # print(headers_files_list[header_idx])
        for data_file in headers_files_list[header_idx + 2 * party_idx]:
            with open(data_file, 'r') as f:
                data = json.load(f)
            header_data += int(data[results_headers[header_idx]]['duration'])
        counter += 1
        ws.write(header_idx + 1, party_idx + 1, header_data // len(headers_files_list[header_idx + 2 * party_idx]))


wb.close()
