"""
The io module contains functions to read/send data and write results to 
files/html reports.
"""
import pandas as pd
import numpy as np
import logging
import os
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
    Read Campbell Scientific CSV file.

    Parameters
    ----------
    file_name : string
        File name, with full path

    index_col : string (optional)
        Index column name, default = 'TIMESTAMP'

    encoding : string (optional)
        Character encoding (i.e. utf-16)
    
    Returns
    ---------
    df : pd.DataFrame
        Data
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
    
def send_email(subject, html_body, recipient, attachment=None):
    """
    Send email via Outlook.
    
    Parameters
    ----------
    subject : string
        Subject text
        
    html_body : string
        HTML body text
    
    recipient : string
        Email address or addresses, separated by semicolon
    
    attachment : string (optional)
        Name of file to attached, with full path
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
    newMail.To = recipient
    if attachment:
        newMail.Attachments.Add(attachment)
    newMail.Send()

def write_metrics(filename, metrics):
    """
    Write metrics file.
    
    Parameters
    -----------
    filename : string
        File name, with full path
    
    metrics : pd.DataFrame
        Data to add to the metrics file
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
    Write test results file.

    Parameters
    -----------
    filename : string
        File name, with full path

    test_results : pd.DataFrame
        Test results stored in pm.test_results
    """

    test_results.sort_values(['System Name', 'Variable Name'], inplace=True)
    test_results.index = np.arange(1, test_results.shape[0]+1)

    logger.info("Writing test results csv file " + filename)

    fout = open(filename, 'w')
    test_results.to_csv(fout, na_rep = 'NaN')
    fout.close()

def write_monitoring_report(filename, pm, test_results_graphics=[], custom_graphics=[], metrics=None, 
                             title='Pecos Monitoring Report', config={}, logo=False, encode=False):
    """
    Generate a monitoring report.  
    The monitoring report is used to report quality control test results for a single system.
    The report includes custom graphics, performance metrics, and test results.
    
    Parameters
    ----------
    filename : string
        File name, with full path

    pm : PerformanceMonitoring object
        Contains data (pm.df) and test results (pm.test_results)
    
    test_results_graphics : list of strings (optional)
        Graphics files, with full path.  These graphics highlight data points 
        that failed a quality control test, created using pecos.graphics.plot_test_results()
        
    custom_graphics : list of strings (optional)
        Custom files, with full path.  Created by the user.
    
    metrics : pd.DataFrame (optional)
        Performance metrics to add as a table to the monitoring report
    
    title : string (optional)
        Monitoring report title, default = 'Pecos Monitoring Report'
        
    config : dictionary (optional)
        Configuration options, to be printed at the end of the report
    
    logo : string (optional)
        Graphic to be added to the report header
    
    encode : boolean (optional)
        Encode graphics in the html, default = False
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
    try:
        logfiledir = logfiledir = os.path.join(dirname(abspath(__file__)))
        f = open(join(logfiledir,'logfile'), 'r')
        notes = f.read()
        f.close()
        notes_df = pd.DataFrame(notes.splitlines())
        notes_df.index += 1
    except:
        notes_df = pd.DataFrame()
    
    pm.test_results.sort_values(['System Name', 'Variable Name'], inplace=True)
    pm.test_results.index = np.arange(1, pm.test_results.shape[0]+1)
    
    # Convert to html format
    if metrics is None:
        metrics = pd.DataFrame()
    test_results_html = pm.test_results.to_html(justify='left')
    metrics_html = metrics.to_html(justify='left')
    notes_html = notes_df.to_html(justify='left', header=False)
    
    sub_dict = {'title': os.path.basename(title),
                'start_time': str(start_time), 
                'end_time': str(end_time), 
                'num_notes': str(notes_df.shape[0]),
                'notes': notes_html, 
                'num_test_results': str(pm.test_results.shape[0]),
                'test_results': test_results_html,
                'test_results_graphics': test_results_graphics,
                'custom_graphics': custom_graphics,
                'num_metrics': str(metrics.shape[0]),
                'metrics': metrics_html,
                'config': config}
    html_string = _html_template_monitoring_report(sub_dict, logo, encode=encode)
    
    # Write html file
    html_file = open(filename,"w")
    html_file.write(html_string)
    html_file.close()
    
    logger.info("")
    
def write_dashboard(filename, column_names, row_names, content, 
                    title='Pecos Dashboard', footnote='', logo=False, encode=False):
    """
    Generate a dashboard.  
    The dashboard is used to compare multiple systems.
    Each cell in the dashboard includes custom system graphics and metrics.
    
    Parameters
    ----------
    filename : string
        File name, with full path
    
    column_names : list of strings
        Column names listed in the order they should appear in the dashboard, i.e. ['location1', 'location2']
        
    row_names : list of strings
        Row names listed in the order they should appear in the dashboard, i.e. ['system1', 'system2']
        
    content : dictionary
        Dashboard content for each cell. 
        
        Dictionary keys are tuples indicating the row name and column name, i.e. ('row name', 'column name'), where 'row name' is in the list row_names and 'column name' is in the list column_names. 
        
        For each key, another dictionary is defined that contains the content to be included in each cell of the dashboard.
        Each cell can contain text, graphics, a table, and an html link.  These are defined using the following keys:
        
        - text (string) =  text at the top of each cell
        - graphics (list of strings) =  a list of graphics file names.  Each file name includes the full path
        - table (string) = a table in html format, for example a table of performance metrics.  DataFrames can be converted to an html string using df.to_html() or df.transpose().to_html().
        - link (string) = html link, with full path
        - link text (string) = the name of the link, i.e. 'Link to monitoring report'
        
        For example::
        
            content = {('row name', 'column name'): {
                'text': 'text at the top', 
                'graphic': ['C:\\\\pecos\\\\results\\\\custom_graphic.jpg'], 
                'table': df.to_html(), 
                'link': 'C:\\\\pecos\\\\results\\\\monitoring_report.html', 
                'link text': 'Link to monitoring report'}}
        
    title : string (optional)
        Dashboard title, default = 'Pecos Dashboard'
    
    footnote : string (optional)
        Text to be added to the end of the report
    
    logo : string (optional)
        Graphic to be added to the report header
    
    encode : boolean (optional)
        Encode graphics in the html, default = False
    """
    
    logger.info("Writing dashboard")
    
    # Set pandas display option     
    pd.set_option('display.max_colwidth', -1)
    pd.set_option('display.width', 40)
    
    html_string = _html_template_dashboard(column_names, row_names, content, title, footnote, logo, encode)
    
    # Write html file
    html_file = open(filename,"w")
    html_file.write(html_string)
    html_file.close()
    
    logger.info("")
    
def _html_template_monitoring_report(sub_dict, logo, encode):
    
    template = """
    <!DOCTYPE html>
    <html lang="en-US">
    <body style="background-color:white;">
    <head>
    <title>$title</title>
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
    <H2>$title</H2>
    """
    #if sub_dict['num_data'] > 0:
    template = template + """
    Start time: $start_time <br>
    End time:  $end_time <br>
    Test Failures: $num_test_results <br>        
    Notes: $num_notes <br>
    <br>"""
    for im in sub_dict['custom_graphics']:
        if encode:
            with open(im, "rb") as f:
                data = f.read()
                img_encode = data.encode("base64")
            template = template + """<img src="data:image/png;base64,"""+img_encode+"""\" alt="Image not loaded" width=\"700\"><br>"""
        else:
            template = template + """<img src=\"""" + im + """\" alt="Image not loaded" width=\"700\"><br>"""
    
    if int(sub_dict['num_metrics']) > 0:
        template = template + """
        <H3>Performance Metrics:</H3>
        $metrics
        <br>"""
        
    if int(sub_dict['num_test_results']) > 0:
        template = template + """
        <H3>Test Results:</H3>
        $test_results
        <br>"""
        for im in sub_dict['test_results_graphics']:
            if encode:
                with open(im, "rb") as f:
                    data = f.read()
                    img_encode = data.encode("base64")
                template = template + """<img src="data:image/png;base64,"""+img_encode+"""\" alt="Image not loaded" width=\"700\"><br>"""
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
    This report was generated by <A href="https://github.com/sandialabs/pecos">Pecos</A> """
    date = datetime.datetime.now()
    datestr = date.strftime('%m/%d/%Y')
    template = template + pecos.__version__ + ", " + datestr
    template = template + """
    </html>"""
    
    template = Template(template)
    
    html_string = template.substitute(sub_dict)
    
    return html_string

def _html_template_dashboard(column_names, row_names, content, title, footnote, logo, encode):
    
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
                        if encode:
                            with open(im, "rb") as f:
                                data = f.read()
                                img_encode = data.encode("base64")
                            template = template + """<img src="data:image/png;base64,"""+img_encode+"""\" alt="Image not loaded" width=\"250"><br>"""
                        else:
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
    This report was generated by <A href="https://github.com/sandialabs/pecos">Pecos</A> """
    date = datetime.datetime.now()
    datestr = date.strftime('%m/%d/%Y')
    template = template + pecos.__version__ + ", " + datestr
    template = template + """
    </html>"""
    
    template = template + """
    </html>"""
    
    return template
