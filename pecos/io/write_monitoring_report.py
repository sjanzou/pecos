import pandas as pd
import numpy as np
import logging
import os
from glob import glob
from os.path import abspath, dirname, join
import pecos.graphics
import datetime
import pprint
from string import Template

logger = logging.getLogger(__name__)

def write_monitoring_report(filename, subdirectory, pm, metrics=None, config={}, logo=False):
    """
    Generate a performance monitoring report
    
    Parameters
    ----------
    filename : string
    
    subdirectory : 
    
    pm : PerformanceMonitoring object
        Contains data (pm.df) and test results (pm.test_results)
        
    metrics : pd.DataFrame (optional)
    
    config : dict (optional)
        Configuration options, to be printed at the end of the report
    
    logo : string (optional)
        Graphic to be added to the report header
    """
    
    logger.info("Writing HTML report")
    
    if pm.df.empty:
        logger.warning("Empty database")
        start_time = 'NaN'
        end_time = 'NaN'
        logger.warning("Empty database")
    else:
        start_time = pm.df.index[0]
        end_time = pm.df.index[-1]
    
    # Set pandas display option     
    pd.set_option('display.max_colwidth', -1)
    pd.set_option('display.width', 40)
    
    # Collect notes (from the logger file)
    logfiledir = logfiledir = os.path.join(dirname(abspath(__file__)),'..', 'logger')
    f = open(join(logfiledir,'logfile'), 'r')
    notes = f.read()
    f.close()
    notes_df = pd.DataFrame(notes.splitlines())
    notes_df.index += 1
    
    pm.test_results.sort(['System Name', 'Variable Name'], inplace=True)
    pm.test_results.index = np.arange(1, pm.test_results.shape[0]+1)
    
    # Generate graphics
    pecos.graphics.plot_test_results(join(subdirectory, 'test'), pm)
    
    # Gather custom graphic
    custom_graphic_files = sorted(glob(abspath(join(subdirectory, '*custom*.jpg'))))

    # Gather test results graphics
    qc_graphic_files = sorted(glob(abspath(join(subdirectory, '*pecos*.jpg'))))
    
    # Convert to html format
    if metrics is None:
        metrics = pd.DataFrame()
    warnings_html = pm.test_results.to_html(justify='left')
    metrics_html = metrics.to_html(justify='left')
    notes_html = notes_df.to_html(justify='left', header=False)
    
    sub_dict = {'database': os.path.basename(subdirectory),
                'start_time': str(start_time), #data.df.index[0]),
                'end_time': str(end_time), #data.df.index[-1]),
                'num_notes': str(notes_df.shape[0]),
                'notes': notes_html, #.replace('\n', '<br>'),
                'num_missing_data': str(0),
                #'missing_data': missing_html,
                'num_warnings': str(pm.test_results.shape[0]),
                'warnings': warnings_html,
                'graphics_path': os.path.abspath(subdirectory),
                'qc_graphics': qc_graphic_files,
                'general_graphics': custom_graphic_files,
                #'num_data': data.df.shape[0],
                'num_metrics': str(metrics.shape[0]),
                'metrics': metrics_html,
                'config': config}
    html_string = _html_template(sub_dict, logo)
    
    # Write html file
    html_file = open(filename,"w")
    html_file.write(html_string)
    html_file.close()
    
    logger.info("")
    
def _html_template(sub_dict, logo, encode_flag=False):
    
    template = """
    <!DOCTYPE html>
    <html lang="en-US">
    <head>
    <title>$database</title>
    <meta charset="UTF-8" />
    </head>
    <table border="0" width="100%">
    <col style="width:70%">
    <col style="width:30%">
    <tr>
    <td align="left" valign="center">"""
    if logo:
        template = template + """
        <img  src=\"""" + logo + """\" alt='Logo' />"""

    template = template + """
    </td>
    <td align="right" valign="center">"""
    template = template + """ 
    </td>
    </tr>
    </table>
    <hr>
    <H2>$database Report</H2>
    """
    #if sub_dict['num_data'] > 0:
    template = template + """
    Start time: $start_time <br>
    End time:  $end_time <br>
    Test Failures: $num_warnings <br>        
    Notes: $num_notes <br>
    <br>"""
    for im in sub_dict['general_graphics']:
        if encode_flag:
            with open(im, "rb") as f:
                data = f.read()
                img_encode = data.encode("base64")
            template = template + """<img src="data:image/png;base64,"""+img_encode+"""\" alt="Image not loaded" width=\"500\"><br>"""
        else:
            template = template + """<img src=\"""" + im + """\" alt="Image not loaded" width=\"700\"><br>"""
    
    if int(sub_dict['num_metrics']) > 0:
        template = template + """
        <H3>Performance Metrics:</H3>
        $metrics
        <br>"""
        
    #if sub_dict['num_data'] > 0:
    if int(sub_dict['num_missing_data']) > 0:
        template = template + """
        <H3>Missing/Corrupt Data:</H3>
        $missing_data
        <br>"""
    if int(sub_dict['num_warnings']) > 0:
        template = template + """
        <H3>Test Results:</H3>
        $warnings
        <br>"""
        for im in sub_dict['qc_graphics']:
            if encode_flag:
                with open(im, "rb") as f:
                    data = f.read()
                    img_encode = data.encode("base64")
                template = template + """<img src="data:image/png;base64,"""+img_encode+"""\" alt="Image not loaded" width=\"500\"><br>"""
            else:
                template = template + """<img src=\"""" + im + """\" alt="Image not loaded" width=\"700\"><br>"""
    
    if int(sub_dict['num_notes']) > 0:
        template = template + """
        <H3>Notes:</H3>
        $notes <br>
        <br>"""
    else:
        template = template + """
        <H3>Notes:</H3> None<br><br>"""
    
    if sub_dict['config']:
        config = pprint.pformat(sub_dict['config'])
        template = template + """
        <b>Configuration Options:</b><br>
        <pre>""" + config + """</pre><br><br>"""
    
    template = template + """<hr>
    This report was generated by <A href="https://pypi.python.org/pypi/pecos">Pecos</A> """
    date = datetime.datetime.now()
    datestr = date.strftime('%m/%d/%Y')
    template = template + pecos.__version__ + ", " + datestr
    template = template + """
    </html>"""
    
    template = Template(template)
    
    html_string = template.substitute(sub_dict)
    
    return html_string