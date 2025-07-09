import logging
from py2dcos.core.validators import (
    validate_method,
    validate_extension,
    UnsupportedExtensionError,
    UnsupportedMethodError,
)
from py2dcos.core.correlation_model import CorrelationModel

class AppController:
    def __init__(self):
        # remember last parameters to avoid redundant work
        self.prev_state = None
        # will hold the CorrelationModel instance
        self.correlation_obj = None

    def build_model(self, file1, file2='', status=''):
        # if no second file given, use the first for homocorrelation
        if not file2 or isinstance(file2, str):
            file2 = file1

        # validate file extensions and calculation method
        try:
            validate_extension(file1[1], file2[1])
            validate_method(status.get("calcMethod", "HT"))
        except (UnsupportedExtensionError, UnsupportedMethodError) as e:
            logging.error(str(e))
            # re-raise so GUI can show an error dialog
            raise

        # snapshot of inputs to detect changes
        current_state = [file1, 
                         file2, 
                         status['sigmaGaussian'], 
                         status['node_attenuation'], 
                         status['calcMethod'], 
                         status['refSpectra'], 
                         status['reconstruction_components']]

        # only recreate model if any parameter has changed
        if self.prev_state != current_state:
            logging.info("Creating new correlation object.")
            self.correlation_obj = CorrelationModel(
                file1, 
                file2, 
                ref=status['refSpectra'], 
                method=status['calcMethod'], 
                reconstruction_comps=status['reconstruction_components'], 
                sigma_gaussian=status['sigmaGaussian'], 
                node_attenuation=status['node_attenuation'])
            self.prev_state = current_state

        # run synchronous correlation
        logging.info("Calculating synchronous correlation.")
        self.correlation_obj.syn(method=status['calcMethod'])
        logging.info("Calculating asynchronous correlation.")
        self.correlation_obj.asyn(method=status['calcMethod'])

        # return the ready-to-plot model
        return self.correlation_obj