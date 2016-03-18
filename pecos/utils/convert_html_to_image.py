import pandas as pd
import numpy as np
from pandas.tseries.frequencies import to_offset
import logging
import os

logger = logging.getLogger(__name__)

def convert_html_to_image(html_filename, image_filename, image_format='jpg', quality=100, zoom=1):
    """
    Convert html file to impage file using wkhtmltoimage
    See http://wkhtmltopdf.org/ for more information
    
    Parameters
    ----------
    html_filename : string
        HTML filename with full path
    
    image_filename : string
        Image filename with full path
    
    image_format : string  (default = 'jpg')
        Image format
    
    quality : int (default = 100)
        Image quality 
    
    zoom : int (default = 1)
        Zoom factor
    """
    os.system('wkhtmltoimage --format ' + image_format + 
                           ' --quality ' + quality + 
                           ' --zoom ' + zoom + ' ' + 
                            html_filename + ' ' + image_filename)
