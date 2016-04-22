import logging
from os.path import abspath, dirname, join
logging.getLogger('pecos').addHandler(logging.NullHandler())

def initialize():
    pecos_logger = logging.getLogger('pecos')
    fh = logging.FileHandler(join(dirname(abspath(__file__)),'logfile'), mode='w') #, maxBytes=20, backupCount=5)  
    
    pecos_logger.setLevel(logging.DEBUG)
    # warnings/notes are sent to the final report using the logfile
    fh.setLevel(logging.WARNING)
    # all info is sent to the screen
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    if not len(pecos_logger.handlers):
        pecos_logger.addHandler(fh)
        pecos_logger.addHandler(ch)
    
    
