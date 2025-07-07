import logging
from py2dcos.core.validators import validate_method, validate_extension
from py2dcos.core.adapter import Legacy2DWrapper as twoDspecies

class AppController:
    def __init__(self):
        self.prev_state = None
        self.correlation_obj = None

    def calculate_correlation(self, file1, file2='', status=''):
        """
        Given two files and a settings dictionary (status), validate input,
        create or reuse a twoDspecies object, and perform synchronous and asynchronous calculations.

        Parameters:
            file1 (list): [filename, extension] for the first file.
            file2 (list): [filename, extension] for the second file.
            status (dict): Contains settings like 'calcMethod' and 'refSpectra'.

        Returns:
            correlation_obj: Updated twoDspecies object with computed correlations.

        Raises:
            ValueError: If file types or calculation method are invalid.
        """

        if not file2 or isinstance(file2, str):
            file2 = file1


        if not validate_extension(file1[1], file2[1]):
            raise ValueError("Unsupported file types.")
        if not validate_method(status['calcMethod']):
            raise ValueError("Invalid calculation method.")

        # Create a snapshot of the current state.
        current_state = [file1, file2, status['sigmaGaussian'], status['node_attenuation'], status['calcMethod'], status['refSpectra'], status['reconstruction_components']]

        # Recreate the correlation object only if the state has changed.
        if self.prev_state != current_state:
            logging.info("Creating new correlation object.")
            print(file1)
            self.correlation_obj = twoDspecies(file1, file2, ref=status['refSpectra'], method=status['calcMethod'], reconstruction_comps=status['reconstruction_components'], sigma_gaussian=status['sigmaGaussian'], node_attenuation=status['node_attenuation'])
            self.prev_state = current_state

        # Perform the correlation calculations.
        logging.info("Calculating synchronous correlation.")
        self.correlation_obj.syn(method=status['calcMethod'])
        logging.info("Calculating asynchronous correlation.")
        self.correlation_obj.asyn(method=status['calcMethod'])

        return self.correlation_obj