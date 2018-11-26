import os
import glob
import json
import time
import smtplib
from pathlib import Path
from os.path import exists
from os.path import basename

from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import NamedStyle

from collections import OrderedDict

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


class Analyze:
    def __init__(self, protocol_config):
        self.protocol_config = protocol_config
        self.protocol_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.style1 = NamedStyle(number_format='#.##')

    def download_data(self):
        remote_directory = self.protocol_config['workingDirectory']
        is_external = json.loads(self.protocol_config['isExternal'].lower())

        for dir in remote_directory:
            results_path = self.protocol_config['resultsDirectory']
            os.system('fab -f Execution/fabfile.py collect_results:%s,%s,%s --parallel --no-pty'
                      % (dir, results_path, is_external))
            # wait for all clients to download data
            time.sleep(10)

    def send_email(self):
        protocol_name = self.protocol_config['protocol']
        users = list(self.protocol_config['emails'].values())
        configurations = list(self.protocol_config['configurations'].values())
        regions = list(self.protocol_config['regions.json'].values())
        address_me = 'biu.cyber.experiments@gmail.com'
        me = 'BIU Cyber Experiments <biu.cyber.experiments@gmail.com>'

        results_file_name = 'ExperimentReport/Results_%s_%s.xlsx' % (protocol_name, self.protocol_time)

        message = MIMEMultipart()
        message['Subject'] = 'Experiment results for protocol %s' % protocol_name
        message['From'] = me
        message['To'] = ', '.join(users)
        message_body = 'Results for protocol %s are attached.\n' % protocol_name
        message_body += 'The configuration(s) for this experiment are:\n\n'

        # write all the configuration to mail
        for conf in configurations:
            vals = conf.split('@')
            values_str = ''

            for val in vals:
                values_str += '%s ' % val
            message_body += '%s\n' % values_str
        # write all regions.json to mail
        message_body += 'The region(s) the experiment executed are:\n\n'
        for region in regions:
            message_body += '%s\n' % region

        message_body += '\nBIU Cyber Experiments'
        message.attach(MIMEText(message_body))

        # attach to mail all the reports file
        with open(results_file_name, 'rb') as fli:
            part = MIMEApplication(fli.read(), Name=basename(results_file_name))
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(results_file_name)
            message.attach(part)

        with open('../GlobalConfigurations/tokens.json', 'r') as tokens:
            data = json.load(tokens)
            mail_username = data['mail']['user']
            mail_password = data['mail']['password']

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(mail_username, mail_password)
        server.sendmail(me, users, message.as_string())
        server.quit()

    def analyze_results(self, files_list, analysis_type):
        protocol_name = self.protocol_config['protocol']

        results_file_name = 'ExperimentReport/Results_%s_%s.xlsx' % (protocol_name, self.protocol_time)
        parties = set()
        for file in files_list:
            parties.add(int(basename(file.split('*')[3])))

        parties = list(parties)
        parties.sort()

        # parsing tasks names from json file
        # Assumption : all the parties measure the same tasks

        tasks_names = dict()
        print(files_list)

        # load one of the data files to receive the headers to the xlsx file

        with open(files_list[0], 'r') as f:
            data = json.load(f)

        # init list values
        for i in range(len(data)):
            tasks_names[data[i]['name']] = list()

        num_of_repetitions = self.protocol_config['numOfInternalRepetitions']

        if not exists(results_file_name):
            wb = Workbook(write_only=False)
            ws = wb.active
            wb.remove(ws)
        else:
            wb = load_workbook(results_file_name)

        ws = wb.create_sheet(analysis_type)
        ws.cell(row=1, column=1, value='Phase/Number of Parties')

        files_list.sort()

        # counter = 0
        for party_idx in range(len(parties)):
            ws.cell(row=1, column=party_idx + 2, value=parties[party_idx])

            for data_file in files_list:
                if 'numOfParties=%s.json' % str(parties[party_idx]) in data_file:
                    with open(data_file, 'r') as df:
                        json_data = json.load(df, object_pairs_hook=OrderedDict)
                        for json_size_idx in range(len(json_data)):
                            for rep_idx in range(num_of_repetitions):
                                tasks_names[json_data[json_size_idx]['name']].append(
                                    json_data[json_size_idx]['iteration_%s' % str(rep_idx)])
            # write data to excel
            counter = 1
            for key in tasks_names.keys():
                if len(tasks_names) > 0:
                    ws.cell(row=counter + 1, column=1, value=key)
                    ws.cell(row=counter + 1, column=party_idx + 2, value=sum(tasks_names[key]) / len(tasks_names[key]))
                    counter += 1

            # delete all the data from the lists after finish iterate al over party data
            for val in tasks_names.values():
                val.clear()

        wb.save(results_file_name)

    def analyze_cpu(self, results_path):
        files_list = glob.glob(('%s/%s/*cpu*.json' % (Path.home(), results_path)))
        self.analyze_results(files_list, 'cpu')

    def analyze_comm_sent(self, results_path):
        files_list = glob.glob(('%s/%s/*commSent*.json' % (Path.home(), results_path)))
        self.analyze_results(files_list, 'sent')

    def analyze_comm_received(self, results_path):
        files_list = glob.glob(('%s/%s/*commReceived*.json' % (Path.home(), results_path)))
        self.analyze_results(files_list, 'received')

    def analyze_memory(self, results_path):
        files_list = glob.glob(('%s/%s/*memory*.json' % (Path.home(), results_path)))
        self.analyze_results(files_list, 'memory')

    def analyze_all(self):
        results_path = input('Enter results directory. current path is: %s): ' % os.getcwd())
        self.analyze_cpu(results_path)
        to_send = input('Do you want to send the results to email? (y/n):')
        if to_send == 'y':
            self.send_email()
