import json
from urllib.request import urlopen
from Execution import end_to_end as e2e


class Submission:

    def __init__(self, config_file_address):
        response = urlopen(config_file_address)
        data = response.read().decode('utf-8')
        self.submission_data = json.loads(data)
        self.config_file_path = config_file_address

    def validate(self):
        for cp in self.submission_data['CloudProviders'].keys():
            self.submission_data['CloudProviders'][cp]['regions'] = ['local']
        execution = e2e.E2E(self.submission_data, self.config_file_path)
        execution.install_experiment()

