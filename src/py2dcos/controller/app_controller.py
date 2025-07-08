import logging
from py2dcos.core.validators import (
    validate_method,
    validate_extension,
    UnsupportedExtensionError,
    UnsupportedMethodError,
)
from py2dcos.core.correlation_model import CorrelationModel as twoDspecies

class AppController:
    def __init__(self):
        self.prev_state = None
        self.correlation_obj = None

    def build_model(self, file1, file2='', status=''):
        if not file2 or isinstance(file2, str):
            file2 = file1

        # Validate
        try:
            validate_extension(file1[1], file2[1])
            validate_method(status.get("calcMethod", "HT"))
        except (UnsupportedExtensionError, UnsupportedMethodError) as e:
            logging.error(str(e))
            # propagate to GUI; it already shows a QMessageBox
            raise

        # Create a snapshot of the current state.
        current_state = [file1, 
                         file2, 
                         status['sigmaGaussian'], 
                         status['node_attenuation'], 
                         status['calcMethod'], 
                         status['refSpectra'], 
                         status['reconstruction_components']]

        # Recreate the correlation object only if the state has changed.
        if self.prev_state != current_state:
            logging.info("Creating new correlation object.")
            self.correlation_obj = twoDspecies(
                file1, 
                file2, 
                ref=status['refSpectra'], 
                method=status['calcMethod'], 
                reconstruction_comps=status['reconstruction_components'], 
                sigma_gaussian=status['sigmaGaussian'], 
                node_attenuation=status['node_attenuation'])
            self.prev_state = current_state

        # Perform the correlation calculations.
        logging.info("Calculating synchronous correlation.")
        self.correlation_obj.syn(method=status['calcMethod'])
        logging.info("Calculating asynchronous correlation.")
        self.correlation_obj.asyn(method=status['calcMethod'])

        return self.correlation_obj