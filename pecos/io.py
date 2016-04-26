"""
The io module contains functions to read/send data and write results to 
files/html reports.
"""
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

try:
    from nose.tools import nottest as _nottest
except ImportError:
    def _nottest(afunction):
        return afunction
        
logger = logging.getLogger(__name__)

def read_campbell_scientific(file_name, index_col='TIMESTAMP', encoding=None):
    """
    Read Campbell Scientific CSV file

    Parameters
    ----------
    file_name : string
        File name with full path

    index_col : string
        Index column name

    encoding : string
        Character encoding (i.e. utf-16)
    """
    logger.info("Reading Campbell Scientific CSV file " + file_name)

    try:
        df = pd.read_csv(file_name, skiprows=1, encoding=encoding, index_col=index_col, parse_dates=True, dtype=unicode) #, low_memory=False)
        df = df[2:]
        index = pd.to_datetime(df.index)
        Unnamed = df.filter(regex='Unnamed')
        df = df.drop(Unnamed.columns, 1)
        df = pd.DataFrame(data = df.values, index = index, columns = df.columns, dtype='float64')
    except:
        logger.warning("Cannot extract database, CSV file reader failed " + file_name)
        df = pd.DataFrame()
        return

    # Drop rows with NaT (not a time) in the index
    try:
        df.drop(pd.NaT, inplace=True)
    except:
        pass

    return df
    
def send_email(subject, html_body, recipeint, attachment=None):
    """
    Send email via Outlook
    
    Parameters
    ----------
    subject : string
        Subject text
        
    html_body : string
        HTML body text
    
    recipeint : string
        Email address or addresses, separated by semicolon
    
    attachment : string
        Name of file to attached (with full path)
    """
    try:
        import win32com.client
    except:
        logger.info('Could not import win32com.client')
        return

    logger.info("Sending email")
    
    olMailItem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    newMail = obj.CreateItem(olMailItem)
    newMail.Subject = subject
    newMail.HTMLBody = html_body
    newMail.To = recipeint
    if attachment:
        newMail.Attachments.Add(attachment)
    newMail.Send()

def write_metrics(filename, metrics):
    """
    Write metrics file
    
    Parameters
    -----------
    filename : string
        Filename with full path
    
    metrics : pd.Series
        Data to add to the stats file
    """
    logger.info("Write metrics file")

    try:
        previous_metrics = pd.read_csv(filename, index_col='TIMESTEP', parse_dates=True)
    except:
        previous_metrics = pd.DataFrame()
    
    metrics = metrics.combine_first(previous_metrics) 
    
    fout = open(filename, 'w')
    metrics.to_csv(fout, index_label='TIMESTEP', na_rep = 'NaN')
    fout.close()

@_nottest
def write_test_results(filename, test_results):
    """
    Write test results file

    Parameters
    -----------
    filename : string
        Filename with full path

    test_results : pd.DataFrame
        Test results stored in pm.test_results
    """

    test_results.sort_values(['System Name', 'Variable Name'], inplace=True)
    test_results.index = np.arange(1, test_results.shape[0]+1)

    logger.info("Writing test results csv file " + filename)

    fout = open(filename, 'w')
    test_results.to_csv(fout, na_rep = 'NaN')
    fout.close()

def write_monitoring_report(filename, subdirectory, pm, metrics=None, config={}, logo=False):
    """
    Generate a performance monitoring report
    
    Parameters
    ----------
    filename : string
        Filename with full path
    
    subdirectory : string
        Full path to directory containing results
    
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
    logfiledir = logfiledir = os.path.join(dirname(abspath(__file__)))
    f = open(join(logfiledir,'logfile'), 'r')
    notes = f.read()
    f.close()
    notes_df = pd.DataFrame(notes.splitlines())
    notes_df.index += 1
    
    pm.test_results.sort_values(['System Name', 'Variable Name'], inplace=True)
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
    html_string = _html_template_monitoring_report(sub_dict, logo)
    
    # Write html file
    html_file = open(filename,"w")
    html_file.write(html_string)
    html_file.close()
    
    logger.info("")

def write_dashboard(filename, column_names, row_names, content, title='Pecos Dashboard', footnote='', logo=False):
    """
    Generate a Pecos report
    
    Parameters
    ----------
    filename : string
    
    content : pd.DataFrame
    
    title : string (optional, default = 'Pecos Dashboard')
    
    footnote : string (optional, default = no footer)
    
    logo : string (optional, default = no logo)
        Graphic to be added to the report header
    """
    
    logger.info("Writing dashboard")
    
    # Set pandas display option     
    pd.set_option('display.max_colwidth', -1)
    pd.set_option('display.width', 40)
    
    html_string = _html_template_dashboard(column_names, row_names, content, title, footnote, logo)
    
    # Write html file
#    filename = join('Results', 'dashboard_' + title + ".html")
    html_file = open(filename,"w")
    html_file.write(html_string)
    html_file.close()
    
    logger.info("")
    
def _html_template_monitoring_report(sub_dict, logo, encode_flag=False):
    
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

def _html_template_dashboard(column_names, row_names, content, title, footnote, logo):
    
    template = """
    <!DOCTYPE html>
    <html lang="en-US">
    <head>
    <title>"""
    template = template + title
    template = template + """
    </title>
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
    <H2>"""
    template = template + title
    template = template + """
    </H2>
    <table border="1" class="dataframe">
    <thead>
    <tr>
    <th></th>"""
    for column in column_names:
        template = template +  """
        <th align="center" valign="middle">""" + column + """</th>"""
    template = template + """
    </tr>
    </thead>
    <tbody>"""
    for row in row_names:
        template = template + """
        <tr>"""
        template = template +  """
        <th align="center" valign="middle">""" + row + """</th>"""
        for column in column_names:
            template = template + """
            <td align="center" valign="middle">"""
            try:
                content[row, column]
                # Add text
                if content[row, column]['text']:
                    template = template + content[row, column]['text'] + """<br>"""
                # Add graphics
                if len(content[row, column]['graphics']) > 0:
                    for im in content[row, column]['graphics']:
                        template = template + """<img src=\"""" + im + """\" alt="Image not loaded" width=\"250"><br>"""
                # Add table
                if content[row, column]['table']:
                    template = template + content[row, column]['table'] + """<br>"""
                # Add link
                if content[row, column]['link']:
                    template = template + """<A href=\"""" + content[row, column]['link'] + """\">""" + content[row, column]['link text'] + """</A>"""
            except:
                pass
            template = template + """</td>"""
       
        template = template + """
        </tr>"""
   
    template = template + """
    </tbody>
    </table> 
    <br>"""
    template = template + footnote + """<br><br>"""
    template = template + """<hr>
    This report was generated by <A href="https://pypi.python.org/pypi/pecos">Pecos</A> """
    date = datetime.datetime.now()
    datestr = date.strftime('%m/%d/%Y')
    template = template + pecos.__version__ + ", " + datestr
    template = template + """
    </html>"""
    
    template = template + """
    </html>"""
    
    return template
