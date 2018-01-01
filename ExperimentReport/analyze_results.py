import sys
import os
import glob
import json
import time
import smtplib
from os.path import expanduser
import xlsxwriter.styles
from os.path import basename
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from collections import OrderedDict


config_file_path = sys.argv[1]
results_path = sys.argv[2]

with open(config_file_path) as conf_file:
    conf_data = json.load(conf_file)


def send_email(file_name):

    users = list(conf_data['users'].values())

    protocol_name = conf_data['protocol']
    me = 'BIU Cyber Experiments <biu.cyber.experiments@gmail.com>'

    message = MIMEMultipart()
    message['Subject'] = 'Experiment results for protocol %s' % protocol_name
    message['From'] = me
    message['To'] = ', '.join(users)
    message_body = 'Results for protocol %s are attached.' % protocol_name
    message.attach(MIMEText(message_body))

    with open(file_name, 'rb') as fli:
        part = MIMEApplication(fli.read(), Name=basename(file_name))
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_name)
        message.attach(part)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(me, 'CyberExp')
    server.sendmail(me, users, message.as_string())
    server.quit()


def upload_to_git(results_file_name):
    protocol_name = conf_data['protocol']
    working_dir = '%s/ExperimentsResults/%s' % (expanduser('~'), protocol_name)
    # create working directory for the protocol if not exist

    os.system('mkdir -p %s ' % working_dir)

    # move the results folder and the xlsx file to the protocol folder

    os.system('mv %s %s' % (results_path, working_dir))
    os.system('mv %s %s' % (results_file_name, working_dir))

    # Upload data to git

    os.curdir(expanduser('~/ExperimentsResults'))
    os.system('git add %s/%s %s/%s' % (protocol_name, results_path, protocol_name, results_file_name))
    os.system('git commit -m "Add results for protocol %s' % protocol_name)
    os.system('git push git@github.com:cryptobiu/ExperimentsResults.git')


def analyze_results():
    results_directory = results_path
    files_list = glob.glob(expanduser('%s/*.json' % results_directory))

    parties = set()
    for file in files_list:
        parties.add(int(file.split('_')[3].split('.')[0].split('=')[1]))

    parties = list(parties)
    parties.sort()

    # parsing tasks names from json file
    # Assumption : all the parties measure the same tasks

    tasks_names = dict()

    # load one of the data files to receive the headers to the xlsx file

    with open(files_list[0], 'r') as f:
        data = json.load(f)

    # init list values
    for i in range(len(data)):
        tasks_names[data[i]['name']] = list()

    protocol_name = conf_data['protocol']
    num_of_repetitions = conf_data['numOfInternalRepetitions']

    protocol_time = str(time.time())
    results_file_name = 'Results/Results_%s_%s.xlsx' % (protocol_name, protocol_time)
    wb = xlsxwriter.Workbook(results_file_name)
    style1 = wb.add_format({'num_format': '#.##'})

    ws = wb.add_worksheet(protocol_name)
    ws.write(0, 0, 'Phase/Number of Parties')

    files_list.sort()

    # counter = 0
    for party_idx in range(len(parties)):
        ws.write(0, party_idx + 1, parties[party_idx])

        for data_file in files_list:
            if 'numOfParties=%s.json' % str(parties[party_idx]) in data_file:
                with open(data_file, 'r') as df:
                    json_data = json.load(df, object_pairs_hook=OrderedDict)
                    for json_size_idx in range(len(json_data)):
                        for rep_idx in range(num_of_repetitions):
                            tasks_names[json_data[json_size_idx]['name']].append(
                                json_data[json_size_idx]['iteration_%s' % str(rep_idx)])
        # write data to excel
        counter = 0
        for key in tasks_names.keys():
            if len(tasks_names) > 0:
                ws.write(counter + 1, 0, key, style1)
                ws.write(counter + 1, party_idx + 1,
                         sum(tasks_names[key]) / len(tasks_names[key]), style1)
                counter += 1

        # delete all the data from the lists after finish iterate al over party data
        for val in tasks_names.values():
            val.clear()

    wb.close()

    send_email(results_file_name)

    upload_to_git(results_file_name)


analyze_results()
