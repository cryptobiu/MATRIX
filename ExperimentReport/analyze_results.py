import os
import sys
import glob
import json
import time
from os.path import expanduser
import xlsxwriter.styles
import smtplib
from os.path import basename
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart


config_file_path = sys.argv[1]
results_path = sys.argv[2]

with open(config_file_path) as conf_file:
    conf_data = json.load(conf_file)


def send_email(file_name):

    protocol_name = conf_data['protocol']
    user = conf_data['user']
    me = 'liork.cryptobiu@gmail.com'

    message = MIMEMultipart()
    message['Subject'] = 'Experiment results for protocol %s' % protocol_name
    message['From'] = me
    message['To'] = user
    message_body = 'Results for protocol %s are attached.' % protocol_name
    message.attach(MIMEText(message_body))

    with open(file_name, 'rb') as fli:
        part = MIMEApplication(fli.read(), Name=basename(file_name))
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_name)
        message.attach(part)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(me, 'Orange12!@')
    server.sendmail(me, user, message.as_string())
    server.quit()


def analyze_results():
    results_directory = results_path
    print('***********************')
    print(results_path)
    files_list = glob.glob(expanduser('%s/*.json' % results_directory))

    parties = set()
    for file in files_list:
        parties.add(int(file.split('_')[5].split('.')[0].split('=')[1]))

    results_headers = set()
    for file in files_list:
        results_headers.add(file.split('_')[3])

    parties = list(parties)
    results_headers = list(results_headers)

    headers_files_list = list()

    # split files according to their task name
    for party in parties:
        for header in results_headers:
            files_headers = list()
            for file in files_list:
                if header in file and 'numberOfParties=%s' % str(party) in file:
                    files_headers.append(file)
            headers_files_list.append(files_headers)

    # results_directory = conf_data['resultsDirectory']
    protocol_name = conf_data['protocol']

    protocol_time = str(time.time())
    results_file_name = 'Results/Results_%s_%s.xlsx' % (protocol_name, protocol_time)
    wb = xlsxwriter.Workbook(results_file_name)
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
            ws.write(header_idx + 1, party_idx + 1, header_data // len(headers_files_list[header_idx + 2 * party_idx]),
                     style1)

    # create chart
    chart = wb.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
    # categories are X axis, values are Y axis
    # [sheetname, first_row, first_col, last_row, last_col]
    chart.add_series({'categories': [protocol_name, 0, 0, len(results_headers), len(parties)],
                      'values': [protocol_name, 0, 0, len(results_headers), len(parties)]}
                     )
    print(len(results_headers))
    print(len(parties))

    ws.insert_chart('A12', chart)

    wb.close()

    # send_email(results_file_name)
    #
    # os.system('git add Results/Results_%s_%s.xlsx' % (protocol_name, protocol_time))
    # os.system('git commit -m \"Add results file for Experiment: %s\"' % protocol_name)
    # os.system('git push https://liorbiu:4aRotdy0vOhfvVgaUaSk@github.com/cryptobiu/MATRIX')


analyze_results()

