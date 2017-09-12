import subprocess


class PreProcess:

    def create_circuits(self):
        phandles = list()
        phandles.append(subprocess.Popen(['ExpirementExecute/GenerateArythmeticCircuitForDepthAndGates.jar', '100',
                                          '100', '10', '10', '50', '0', 'true'], shell=False))
        exit_codes = [p.wait() for p in phandles]
        return exit_codes[0]
