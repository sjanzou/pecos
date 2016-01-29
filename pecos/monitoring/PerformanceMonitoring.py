import pandas as pd
import numpy as np
import re
import logging

none_list = ['','none','None','NONE', None, [], {}]
nan_list = ['nan','NaN','NAN']

logger = logging.getLogger(__name__)
    
class PerformanceMonitoring(object):

    def __init__(self):
        """
        Performance Monitoring class
        """
        self.df = pd.DataFrame()
        self.trans = {}
        self.tfilter = pd.Series()
        self.test_results = pd.DataFrame(columns=['System Name', 'Variable Name', 
                                                'Start Date', 'End Date', 
                                                'Timesteps', 'Error Flag']) 
    
    def add_dataframe(self, df, system_name):
        """
        Add dataframe to the PerformanceMonitoring class
        
        Parameters
        -----------
        df : pd.Dataframe
        """
        temp = df.copy()
        
        # Combine variable name with system name (System: Variable)
        temp.columns = [system_name + ':' + s  for s in temp.columns]
        
        if self.df is not None:
            self.df = self.df.combine_first(temp)
        else:
            self.df = temp.copy()     

        # define identifty translation
        trans = {}
        for col in df.columns:
            trans[col] = [col]
        
        self.add_translation_dictonary(trans, system_name)
            
    def add_translation_dictonary(self, trans, system_name):
        """
        Add translation dictonary to the PerformanceMonitoring class
        
        Parameters
        -----------
        trans : dictonary
        
        system_name : string
        """    
        # Combine variable name with system name (System: Variable)
        for key, values in trans.iteritems():
            self.trans[key] = []
            for value in values:
                self.trans[key].append(system_name + ':' + value)
        
    def add_time_filter(self, time_filter):
        """
        Add a time filter to the PerformanceMonitoring class
        
        Parameters
        ----------
        time_filter : pd.Series
        """
        if isinstance(time_filter, pd.DataFrame):
            self.tfilter = pd.Series(data = time_filter.values[:,0], index = self.df.index)
        else:
            self.tfilter = time_filter
            
#    def add_tfilter(self, composite_eq, specs={}):
#        """
#        Add a time filter to the PerformanceMonitoring class
#        
#        Parameters
#        ----------
#        composite_eq : string
#            Composite equation for tfilter
#        
#        specs : dict
#            Constants to use in the composite equation
#        """
#        if self.df.empty:
#            return
#            
#        logger.info("Create composite signal: tfilter")
#                
#        composite_signal = self.evaluate_string('', composite_eq, specs)
#        self.tfilter = pd.Series(data = composite_signal.values[:,0], index = self.df.index)
    
    def add_signal(self, col_name, df):
        """
        Add signal to the PerformanceMonitoring dataframe
        
        Parameters
        -----------
        col_name : string
            Column name
        
        df : pd.DataFarame
            Data
        """
        df = pd.DataFrame(df)
        
        if col_name in self.trans.keys():
            logger.info(col_name + ' already exists in trans')
            return
        for col in df.columns.values.tolist():
            if col in self.df.columns.values.tolist():
                logger.info(col + ' already exists in df')
                return
        try:
            self.trans[col_name] = df.columns.values.tolist()
            #self.df[df.columns] = df
            for col in df.columns:
                self.df[col] = df[col]
        except:
            logger.warning("Add signal failed: " + col_name)
            return
            
    def append_test_results(self, mask, error_msg, min_failures=1, variable_name=True): #, sub_df=None):
        """
        Append QC results to the PerformanceMonitoring class
        
        Parameters
        ----------
        mask : pd.Dataframe
            Result from QC test, boolean values.
        
        error_msg : string
            Error message to store with the QC results
        
        min_failures : int
            Minimum number of consecutive failures required for reporting
        
        variable_name : bool
            Add variable name to QC results (default = True), set to False for timestamp tests
        """
        if len(mask.columns) == 1 and mask.columns[0] == 0:
            sub_df = self.df
        else:
            sub_df = self.df[mask.columns]
        
        # Find blocks
        order = 'col'
        if order == 'col':
            mask = mask.T
            
        np_mask = mask.values
        
        start_nans_mask = np.hstack((np.resize(np_mask[:,0],(mask.shape[0],1)),
                                     np.logical_and(np.logical_not(np_mask[:,:-1]), np_mask[:,1:])
                                     ))
        stop_nans_mask = np.hstack((np.logical_and(np_mask[:,:-1], np.logical_not(np_mask[:,1:])),
                                    np.resize(np_mask[:,-1], (mask.shape[0],1))
                                    ))
    
        start_row_idx,start_col_idx = np.where(start_nans_mask)
        stop_row_idx,stop_col_idx = np.where(stop_nans_mask)
        
        if order == 'col':
            temp = start_row_idx; start_row_idx = start_col_idx; start_col_idx = temp
            temp = stop_row_idx; stop_row_idx = stop_col_idx; stop_col_idx = temp
            #mask = mask.T
        
        block = {'Start Row': list(start_row_idx), 
                 'Start Col': list(start_col_idx), 
                 'Stop Row': list(stop_row_idx), 
                 'Stop Col': list(stop_col_idx)}
                 
        #if sub_df is None:
        #    sub_df = self.df
        
        for i in range(len(block['Start Col'])):
            length = block['Stop Row'][i] - block['Start Row'][i] + 1
            if length >= min_failures:
                if variable_name:
                    var_name = sub_df.icol(block['Start Col'][i]).name
                    system_name = ''
                    temp = var_name.split(':')
                    if len(temp) == 2:
                        var_name = temp[1]
                        system_name = temp[0]
                else:
                    var_name = ''
                    system_name = ''
                s = pd.Series([system_name, \
                               var_name, \
                               sub_df.index[block['Start Row'][i]], \
                               sub_df.index[block['Stop Row'][i]], \
                               length, \
                               error_msg], \
                    index=['System Name', 'Variable Name', 'Start Date', 'End Date', 'Timesteps', 'Error Flag'])
                self.test_results = self.test_results.append(s, ignore_index=True)
        
    def check_timestamp(self, frequency, expected_start_time=None, expected_end_time=None, min_failures=1):
        """
        Check time series for non-monotonic and duplicate timestamps.
        
        Parameters
        ----------
        frequency : int
            Expected timeseries frequency, in seconds
        
        min_failures : int
            Minimum number of consecutive failures required for reporting
        """
        logger.info("Check timestamp")
        
        if self.df.empty:
            logger.info("Empty database")
            return
        if expected_start_time is None:
            expected_start_time = min(self.df.index)
        if expected_end_time is None:
            expected_end_time = max(self.df.index)
            
        rng = pd.date_range(start=expected_start_time, end=expected_end_time, freq=str(frequency) + 's')
        
        # Check to see if timestamp is monotonic   
        mask = pd.TimeSeries(self.df.index).diff() < 0
        mask.index = self.df.index
        mask[mask.index[0]] = False
        mask = pd.DataFrame(mask)
        
        self.append_test_results(mask, 'Nonmonotonic timestamp', variable_name=False, min_failures=min_failures)    
       
        # If not monotonic, sort df by timestamp
        if not self.df.index.is_monotonic:
            self.df = self.df.sort_index()
            #self.df.sort(columns='TEMP', ascending=True, axis=0, inplace=True)
            
        # Check for duplicate timestamps
        mask = pd.TimeSeries(self.df.index).diff() == 0
        mask.index = self.df.index
        mask[mask.index[0]] = False
        mask = pd.DataFrame(mask)

        self.append_test_results(mask, 'Duplicate timestamp', variable_name=False, min_failures=min_failures)
        
        # Drop duplicate timestamps
        self.df['TEMP'] = self.df.index
        self.df.drop_duplicates(subset='TEMP', take_last=False, inplace=True)
        
        # reindex timestamps
        missing = []
        for i in rng:
            if i not in self.df.index:
                missing.append(i)
        self.df = self.df.reindex(index=rng)
        mask = pd.DataFrame(data=self.df.shape[0]*[False], index = self.df.index)
        mask.loc[missing] = True
        self.append_test_results(mask, 'Missing timestamp', variable_name=False, min_failures=min_failures)
        

        del self.df['TEMP']
        
    def check_range(self, bound, key=None, specs={}, rolling_mean=1, min_failures=1):
        """
        Check data range
        
        Parameters
        ----------
        bound : list
            [lower bound, upper bound], None can be used in place of a bound
            
        key : string (default = None (all columns))
            Translation dictonary key
        
        specs : dict (default = {})
            Constants used in bound
        
        rolling_mean : int (default = 1)
            Rolling mean window in number of timesteps
        
        min_failures : int (default = 1)
            Minimum number of consecutive failures required for reporting
        """
        logger.info("Check variable ranges")
        
        if self.df.empty:
            logger.info("Empty database")
            return
            
        tfilter = self.tfilter
        
        # Isolate subset if key is not None
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Range: " + key)
                return 
        else:
            df = self.df 
        
        # Compute moving average
        if rolling_mean > 1:
            df = pd.rolling_mean(df, rolling_mean)
            
        # Evaluate strings for bound values
        for i in range(len(bound)):
            if bound[i] in none_list:
                bound[i] = None
            elif type(bound[i]) is str:
                bound[i] = self.evaluate_string('', bound[i], specs)
        
        # Lower Bound        
        if bound[0] is not None:
            mask = (df < bound[0])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                self.append_test_results(mask, 'Data < lower bound, '+str(bound[0]), min_failures=min_failures) # sub_df=df)
                    
        # Upper Bound   
        if bound[1] is not None:
            mask = (df > bound[1])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                self.append_test_results(mask, 'Data > upper bound, '+str(bound[1]), min_failures=min_failures) #sub_df=df)
        
    def check_increment(self, bound, key=None, specs={}, increment=1, absolute_value=True, rolling_mean=1, min_failures=1):
        """
        Check range on data increments
        
        Parameters
        ----------
        bound : list
            [lower bound, upper bound], None can be used in place of a bound
        
        key : string (default = None (all columns))
            Translation dictonary key
            
        specs : dict (default = {})
            Constants used in bound
        
        increment : int (default = 1)
            Timestep shift used to compute difference
            
        absolute_value : bool (default = True)
            Take the absolute value of the increment data
            
        rolling_mean : int (default = 1)
            Rolling mean window in number of timesteps
        
        min_failures : int (default = 1)
            Minimum number of consecutive failures required for reporting
        """
        logger.info("Check increment range")
        
        if self.df.empty:
            logger.info("Empty database")
            return
            
        tfilter = self.tfilter
        
        # Isolate subset if key is not None
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Increment: " + key)
                return 
        else:
            df = self.df 
            
        # Compute moving average
        if rolling_mean > 1:
            df = pd.rolling_mean(df, rolling_mean)
            
        # Compute interval
        if absolute_value:
            df = np.abs(df.diff(periods=increment))
        else:
            df = df.diff(periods=increment)
            
        # Evaluate strings for bound values
        for i in range(len(bound)):
            if bound[i] in none_list:
                bound[i] = None
            elif type(bound[i]) is str:
                bound[i] = self.evaluate_string('', bound[i], specs)
        
        # Lower Bound        
        if bound[0] is not None:
            mask = (df < bound[0])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                self.append_test_results(mask, 'Increment < lower bound, '+str(bound[0]), min_failures=min_failures) #sub_df=df)
                    
        # Upper Bound   
        if bound[1] is not None:
            mask = (df > bound[1])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                self.append_test_results(mask, 'Increment > upper bound, '+str(bound[1]), min_failures=min_failures) #sub_df=df)
        
    def check_missing(self, key=None, min_failures=1):
        """
        Check for missing data
        
        Parameters
        ----------
        key : string
            Translation dictonary key
        
        min_failures : int
            Minimum number of consecutive failures required for reporting
        """
        logger.info("Check for missing data")
        
        if self.df.empty:
            logger.info("Empty database")
            return
            
        tfilter = self.tfilter
        
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Missing: " + key) 
                return 
        else:
            df = self.df 
        
        mask = pd.isnull(df) # checks for np.nan, np.inf
        
        missing_timestamps = self.test_results[self.test_results['Error Flag'] == 'Missing timestamp']
        for index, row in missing_timestamps.iterrows():
            mask.loc[row['Start Date']:row['End Date']] = False
            
        if not tfilter.empty:
            mask[~tfilter] = False
        
        if mask.sum(axis=1).sum(axis=0) > 0:
            self.append_test_results(mask, 'Missing data', min_failures=min_failures)
        
    def check_corrupt(self, corrupt_values, key=None, min_failures=1):
        """
        Check for corrupt data
        
        Parameters
        ----------
        corrupt_values : list
            List of corrupt data values
            
        key : string
            Translation dictonary key
        
        min_failures : int
            Minimum number of consecutive failures required for reporting
        """
        logger.info("Check for corrupt data")
        
        if self.df.empty:
            logger.info("Empty database")
            return
            
        tfilter = self.tfilter
        
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Corrupt: " + key)
                return 
        else:
            df = self.df 
            
        mask = pd.DataFrame(data = np.zeros(df.shape), index = df.index, columns = df.columns, dtype = bool) # all False
        for i in corrupt_values:
            mask = mask | (df == i)
            
        if not tfilter.empty:
            mask[~tfilter] = False
            
        if mask.sum(axis=1).sum(axis=0) > 0:
            self.df[mask] = np.nan
            self.append_test_results(mask, 'Corrupt data', min_failures=min_failures)
             
    def evaluate_string(self, col_name, string, specs={}):
        """
        Evaluate python string.  [keywords] are expanded to 
        self.df[self.trans[keyword]]
        or 
        specs[keyword]
        
        """

        match = re.findall(r"\[(.*?)\]", string)
        for m in set(match):
            m = m.replace('[','') # check for list
            
            if m == 'ELAPSED_TIME':
                ELAPSED_TIME = self.get_elapsed_time()
                string = string.replace("["+m+"]",m)
            elif m == 'CLOCK_TIME':
                CLOCK_TIME = self.get_clock_time()
                string = string.replace("["+m+"]",m)
            else:
                try:
                    self.df[self.trans[m]]
                    datastr = "self.df[self.trans['" + m + "']]"
                    string = string.replace("["+m+"]",datastr)
                except:
                    try:
                        specs[m]
                        datastr = "specs['" + m + "']"
                        string = string.replace("["+m+"]",datastr)
                    except:
                        pass
                    
        try:
            signal = eval(string)
            if type(signal) is tuple:
                col_name = [col_name + " " + str(i+1)  for i in range(len(signal))]
                signal = pd.concat(signal, axis=1)
                signal.columns = [col_name]
                signal.index = self.df.index
            elif type(signal) is float:
                signal = signal
            else:
                signal = pd.DataFrame(signal)
                if len(signal.columns) == 1:
                    signal.columns = [col_name]
                else:
                    signal.columns = [col_name + " " + str(i+1)  for i in range(signal.shape[1])]
                signal.index = self.df.index
        except:
            signal = None
            logger.warning("Insufficient data for Composite Signals: " + col_name + ' -- ' + string)
                             
        return signal

    def get_elapsed_time(self):
        elapsed_time = ((self.df.index - self.df.index[0]).values)/1000000000 # convert ns to s
        elapsed_time = pd.DataFrame(data=elapsed_time, index=self.df.index, dtype=int)
        
        return elapsed_time
    
    def get_clock_time(self):
        clock_time = ((self.df.index - pd.Timestamp('2016-01-01 00:00:00')).values)/1000000000 # convert ns to s
        clock_time = pd.DataFrame(data=clock_time, index=self.df.index, dtype=int)
        clock_time = np.mod(clock_time, 86400)
        
        return clock_time
    
    def get_test_results_mask(self, key=None):
        """
        Return a mask of data-times that failed a quality control test
        """
        if self.df.empty:
            logger.info("Empty database")
            return
        
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Key not in dataframe")
                return
        else:
            df = self.df 
            
        warning = ~pd.isnull(df)
        for i in self.test_results.index:
            variable = self.test_results.loc[i, 'Variable Name']
            start_date = self.test_results.loc[i, 'Start Date']
            end_date = self.test_results.loc[i, 'End Date']
            error_flag = self.test_results.loc[i, 'Error Flag']
            if error_flag in ['Nonmonotonic timestamp', 'Duplicate timestamp']:
                continue
            if variable == '':
                warning.loc[start_date:end_date] = False
            else:
                warning.loc[start_date:end_date,variable] = False
            
        return warning
        
#    def reindex_dataframe(self, frequency, start_time=None,  end_time=None):
#        """
#        Reindex dataframe with new start and end time
#        
#        Parameters
#        ----------
#        frequency : int
#            time index frequency in seconds
#        
#        start_time : datetime.datetime
#            Start time, i.e. datetime.datetime(2016, 1, 1, 0, 0, 0)
#            
#        end_time : datetime.datetime
#            End time, i.e. datetime.datetime(2016, 1, 1, 23, 59, 59)
#        """
#        if start_time is None:
#            temp = self.df.index[0]
#            start_time = datetime.datetime(temp.year, temp.month, temp.day, temp.hour, temp.minute, temp.second)
#        if end_time is None:
#            temp = self.df.index[-1]
#            end_time = datetime.datetime(temp.year, temp.month, temp.day, temp.hour, temp.minute, temp.second)
#            
#        rng = pd.date_range(start=start_time, end=end_time, freq=str(frequency) + 's')
#        
#        self.df = self.df.reindex(index=rng)
    
#    def remove_unused_columns(self):
#        """
#        Remove data not used in the translation dictonary
#        """
#        # # Remove columns not included in trans
#        col_to_keep = sum(self.trans.values(),[]) 
#        col_to_keep = [col for col in self.df.columns if col in col_to_keep]
#        try:
#            self.df = self.df[col_to_keep]
#        except:
#            logger.warning(col_to_keep + " not found in the database.  Check the translation dictonary.")
#    
    

    
#    def plot_test_results(self):
#        """
#        Create QC graphics.  
#        QC graphics include data that failed a quality control test.
#        """
#        if self.test_results.empty:
#            return
#            
#        import matplotlib.pyplot as plt
#        from pecos.graphics import plot_timeseries
#        
#        filename = os.path.join(self.options.results_subdirectory, self.options.results_subdirectory_root)
#        
#        graphic = 0
#          
#        tfilter = self.tfilter
#        
#        grouped = self.test_results.groupby(['System Name', 'Variable Name'])
#         
#        for name, test_results_group in grouped:
#            if name[1] == ' ':
#                continue
#            elif name[0] == '':
#                col_name = str(name[1])
#            else:
#                col_name = str(name[0]) + ":" + str(name[1])
#            
#            
#            if test_results_group['Error Flag'].all() in ['Duplicate timestamp', 'Missing data', 'Corrupt data', 'Missing timestamp', 'Nonmonotonic timestamp']:
#                continue
#            logger.info("Creating graphic for " + col_name)
#            plt.figure(figsize = (7.0,2.5))
#            plot_timeseries(self.df[col_name], tfilter, test_results_group = test_results_group)
#
#            ax = plt.gca()
#            box = ax.get_position()
#            ax.set_position([box.x0, box.y0, box.width*0.65, box.height])
#            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8) 
#            plt.title(col_name, fontsize=8)
#           
#            plt.savefig(filename +'_pecos_'+str(graphic)+'.jpg', format='jpg', dpi=500)
#            graphic = graphic + 1
#            plt.close()
#
#    def compute_QCI(self):
#        """
#        Compute QC metric
#        
#        Parameters
#        ----------
#        add_metric : bool
#            Add quality control index (QCI) to the stats file
#            
#        Returns
#        -------
#        qci : pd.Series
#            Quality control index (QCI)
#        """
#        logger.info("Compute QCI")
#        
#        tfilter = self.tfilter
#        df = self.df[tfilter]
#        dates = [df.index[0].date() + datetime.timedelta(days=x) for x in range(0, (df.index[-1].date()-df.index[0].date()).days+1)]
#        
#        mask = self.get_test_results_mask()
#        mask = mask[tfilter]
#                
#        stats = pd.DataFrame(index=pd.to_datetime(dates))
#        
#        if mask.empty:
#            for date in dates:
#                stats.loc[date, 'Quality Control Index'] = 0
#        else:
#            for date in dates:
#                mask_date = mask.loc[date.strftime('%m/%d/%Y')]
#                
#                # Quality Control Index
#                QCIndex = mask_date.sum().sum()/float(mask_date.shape[0]*mask_date.shape[1])
#                if np.isnan(QCIndex):
#                    QCIndex = 0
#                stats.loc[date, 'Quality Control Index'] = QCIndex
#        
#        return stats   
#        
##    def group_test_results(self):
##
##        formatted_test_results = pd.DataFrame(columns=self.test_results.columns)
##                                             
##        key = self.test_results['Error Flag']
##        grouped = self.test_results.groupby(key)
##        for error_flag, group in grouped:
##            try:
##                #test_results_md = grouped.get_group(error_flag)
##                grouped2 = group.groupby(['Start Date', 'End Date', 'Timesteps', 'System Name'])
##                for name, group2 in grouped2:
##                    temp = group2['Variable Name']
##                    #var = np.array([v.rsplit(': ').pop() for v in var])
##                    if temp.shape[0] == 1:
##                        var = temp.values[0]
##                    else:
##                        var = []
##                        for key, value in temp.iteritems():
##                            var.append(str(value))
##                    var = str(var)
##                    var = var.replace("'","")
##                    s = pd.Series([name[3], var, str(name[0]), str(name[1]), name[2], error_flag], index=self.test_results.columns)
##                    formatted_test_results = formatted_test_results.append(s, ignore_index=True)  
##            except:
##                pass
##        
##        formatted_test_results.sort(['System Name', 'Variable Name'], inplace=True)
##        formatted_test_results.index = np.arange(1, formatted_test_results.shape[0]+1)
##        
##        self.test_results = formatted_test_results
#    
#    def write_performance_metric_file(self, stats):
#        """
#        Add metric to the stats file
#        
#        Parameters
#        -----------
#        stat : pd.Series
#            Data to add to the stats file
#        """
#        logger.info("Add metric")
#        
#        if self.df.empty:
#            logger.info("Empty database")
#            return
#            
#        fname = os.path.join(self.options.results_directory, self.options.results_subdirectory_root + '_performance_metrics.csv')
#
#        try:
#            previous_stats = pd.read_csv(fname, index_col='TIMESTEP', parse_dates=True)
#        except:
#            previous_stats = pd.DataFrame()
#        
#        stats = stats.combine_first(previous_stats) 
#        
#        self._performance_metrics = stats.loc[stats.index]
#        
#        fout = open(fname, 'w')
#        stats.to_csv(fout, index_label='TIMESTEP', na_rep = 'NaN')
#        fout.close()
#    
#    
#    def write_test_results_file(self):
#        self.test_results.sort(['System Name', 'Variable Name'], inplace=True)
#        self.test_results.index = np.arange(1, self.test_results.shape[0]+1)
#        
#        fname = join(self.options.results_subdirectory, self.options.results_subdirectory_root + "_test_results.csv")
#        logger.info("Writing test results csv file " + fname)
#        fout = open(fname, 'w')
#        #fout.write('Missing Data\n')
#        #missing_data.to_csv(fout, na_rep = 'NaN')
#        #fout.write('Warnings\n')
#        self.test_results.to_csv(fout, na_rep = 'NaN')
#        fout.close()
#        
#    def write_HTML_report(self, config={}, logo=False):
#        """
#        Generate a Pecos report
#        
#        Parameters
#        ----------
#        pm : PerformanceMonitoring object
#            Contains data (pm.df), test results (pm.test_results), and options (pm.options)
#            
#        config : dict (optional)
#            Configuration options, to be printed at the end of the report
#        
#        logo : string (optional)
#            Graphic to be added to the report header
#        """
#        
#        logger.info("Writing HTML report")
#        
#        if self.df.empty:
#            logger.warning("Empty database")
#            start_time = 'NaN'
#            end_time = 'NaN'
#            logger.warning("Empty database")
#        else:
#            start_time = self.df.index[0]
#            end_time = self.df.index[-1]
#        
#        # Set pandas display option     
#        pd.set_option('display.max_colwidth', -1)
#        pd.set_option('display.width', 40)
#        
#        # Collect notes (from the logger file)
#        logfiledir = logfiledir = os.path.join(dirname(abspath(__file__)),'..', 'logger')
#        f = open(join(logfiledir,'logfile'), 'r')
#        notes = f.read()
#        f.close()
#        notes_df = pd.DataFrame(notes.splitlines())
#        notes_df.index += 1
#        
#        self.test_results.sort(['System Name', 'Variable Name'], inplace=True)
#        self.test_results.index = np.arange(1, self.test_results.shape[0]+1)
#        
#        # Generate graphics
#        self.plot_test_results()
#        
#        # Gather custom graphic
#        custom_graphic_files = glob(abspath(join(self.options.results_subdirectory, '*custom*.jpg')))
#    
#        # Gather performance metrics graphic
#        pm_graphic_files = glob(abspath(join(self.options.results_subdirectory, '*performance_metrics*.jpg')))
#        
#        # Gather test results graphics
#        qc_graphic_files = glob(abspath(join(self.options.results_subdirectory, 
#                                             self.options.results_subdirectory_root + '*pecos*.jpg')))
#        
#        # Convert to html format
#        #pd.set_option('display.max_colwidth',60)
#        #pd.options.display.show_dimensions = False
#        warnings_html = self.test_results.to_html(justify='left')
#        metrics_html = self._performance_metrics.to_html(justify='left')
#        notes_html = notes_df.to_html(justify='left', header=False)
#        
#        sub_dict = {'database': self.options.results_subdirectory_root,
#                    'start_time': str(start_time), #data.df.index[0]),
#                    'end_time': str(end_time), #data.df.index[-1]),
#                    'num_notes': str(notes_df.shape[0]),
#                    'notes': notes_html, #.replace('\n', '<br>'),
#                    'num_missing_data': str(0),
#                    #'missing_data': missing_html,
#                    'num_warnings': str(self.test_results.shape[0]),
#                    'warnings': warnings_html,
#                    'graphics_path': os.path.abspath(self.options.results_subdirectory),
#                    'qc_graphics': qc_graphic_files,
#                    'pm_graphics': pm_graphic_files,
#                    'general_graphics': custom_graphic_files,
#                    #'num_data': data.df.shape[0],
#                    'num_metrics': str(self._performance_metrics.shape[0]),
#                    'metrics': metrics_html,
#                    'config': config}
#        html_string = _html_template(sub_dict, logo, encode_flag=False)
#        
#        # Write html file
#        html_fname = join(self.options.results_subdirectory, self.options.results_subdirectory_root + ".html")
#        html_file = open(html_fname,"w")
#        html_file.write(html_string)
#        html_file.close()
#        
#        logger.info("")
#    
##def _format_missing_data(test_results):
##    missing_data = pd.DataFrame(columns=test_results.columns)
##                                         
##    key = test_results['Error Flag']
##    grouped = test_results.groupby(key)
##    try:
##        for error_flag in ['Missing data', 'Missing timestamp', 'Corrupt data']:
##            try:
##                test_results_md = grouped.get_group(error_flag)
##                grouped2 = test_results_md.groupby(['Start Date', 'End Date', 'Timesteps', 'System Name'])
##                #grouped = test_results_md.groupby(['Start Date', 'End Date', 'Timesteps', 0]) #'System Name'])
##                #pd.set_printoptions(max_colwidth=100)
##                for name, group in grouped2:
##                    var = group['Variable Name'].values   
##                    var = np.array([v.rsplit(': ').pop() for v in var])
##                    s = pd.Series([name[3], var, str(name[0]), str(name[1]), name[2], error_flag], index=test_results.columns)
##                    missing_data = missing_data.append(s, ignore_index=True)  
##            except:
##                pass
##
##    except:
##        pass
##    
##    return missing_data
##    
##def _format_test_results(test_results):
##    
##    temp = test_results['Variable Name'].apply(lambda x: pd.Series(x.split(':'))).stack()
##    temp.sortlevel(1)
##    for i in range(test_results.shape[0]):
##        if len(temp[i]) == 2:
##            test_results.loc[i,'System Name'] = temp[i][0]
##            test_results.loc[i,'Variable Name'] = temp[i][1]
##            
##    formatted_test_results = pd.DataFrame(columns=test_results.columns)
##                                         
##    key = test_results['Error Flag']
##    grouped = test_results.groupby(key)
##    for test_results_group in grouped:
##        error_flag = test_results_group[0]
##        try:
##            #test_results_md = grouped.get_group(error_flag)
##            grouped2 = test_results_group.groupby(['Start Date', 'End Date', 'Timesteps', 'System Name'])
##            for name, group in grouped2:
##                var = group['Variable Name'].values   
##                var = np.array([v.rsplit(': ').pop() for v in var])
##                s = pd.Series([name[3], var, str(name[0]), str(name[1]), name[2], error_flag], index=test_results.columns)
##                formatted_test_results = formatted_test_results.append(s, ignore_index=True)  
##        except:
##            pass
##        
##    test_results = formatted_test_results
#    
#def _html_template(sub_dict, logo=False, encode_flag=False):
#    
#    template = """
#    <!DOCTYPE html>
#    <html lang="en-US">
#    <head>
#    <title>$database</title>
#    <meta charset="UTF-8" />
#    </head>
#    <table border="0" width="100%">
#    <col style="width:70%">
#    <col style="width:30%">
#    <tr>
#    <td align="left" valign="center">"""
#    if logo:
#        template = template + """
#        <img  src=\"""" + logo + """\" alt='Logo' />"""
#
#    template = template + """
#    </td>
#    <td align="right" valign="center">"""
#    template = template + """ 
#    </td>
#    </tr>
#    </table>
#    <hr>
#    <H2>$database Report</H2>
#    """
#    #if sub_dict['num_data'] > 0:
#    template = template + """
#    Start time: $start_time <br>
#    End time:  $end_time <br>
#    Test Failures: $num_warnings <br>        
#    Notes: $num_notes <br>
#    <br>"""
#    for im in sub_dict['general_graphics']:
#        if encode_flag:
#            with open(im, "rb") as f:
#                data = f.read()
#                img_encode = data.encode("base64")
#            template = template + """<img src="data:image/png;base64,"""+img_encode+"""\" alt="Image not loaded" width=\"500\"><br>"""
#        else:
#            template = template + """<img src=\"""" + im + """\" alt="Image not loaded" width=\"700\"><br>"""
#    
#    if int(sub_dict['num_metrics']) > 0:
#        template = template + """
#        <H3>Performance Metrics:</H3>
#        $metrics
#        <br>"""
#        for im in sub_dict['pm_graphics']:
#            if encode_flag:
#                with open(im, "rb") as f:
#                    data = f.read()
#                    img_encode = data.encode("base64")
#                template = template + """<img src="data:image/png;base64,"""+img_encode+"""\" alt="Image not loaded" width=\"500\"><br>"""
#            else:
#                template = template + """<img src=\"""" + im + """\" alt="Image not loaded" width=\"700\"><br>"""
#    
#        
#    #if sub_dict['num_data'] > 0:
#    if int(sub_dict['num_missing_data']) > 0:
#        template = template + """
#        <H3>Missing/Corrupt Data:</H3>
#        $missing_data
#        <br>"""
#    if int(sub_dict['num_warnings']) > 0:
#        template = template + """
#        <H3>Test Results:</H3>
#        $warnings
#        <br>"""
#        for im in sub_dict['qc_graphics']:
#            if encode_flag:
#                with open(im, "rb") as f:
#                    data = f.read()
#                    img_encode = data.encode("base64")
#                template = template + """<img src="data:image/png;base64,"""+img_encode+"""\" alt="Image not loaded" width=\"500\"><br>"""
#            else:
#                template = template + """<img src=\"""" + im + """\" alt="Image not loaded" width=\"700\"><br>"""
#    
#    if int(sub_dict['num_notes']) > 0:
#        template = template + """
#        <H3>Notes:</H3>
#        $notes <br>
#        <br>"""
#    else:
#        template = template + """
#        <H3>Notes:</H3> None<br><br>"""
#    
#    if sub_dict['config']:
#        config = pprint.pformat(sub_dict['config'])
#        template = template + """
#        <b>Configuration Options:</b><br>
#        <pre>""" + config + """</pre><br><br>"""
#    
#    template = template + """
#    This report was generated by <A href="https://pypi.python.org/pypi/pecos">Pecos</A> """
#    date = datetime.datetime.now()
#    datestr = date.strftime('%m/%d/%Y')
#    template = template + pecos.__version__ + ", " + datestr
#    template = template + """
#    <hr>
#    </html>"""
#    
#    template = Template(template)
#    
#    html_string = template.substitute(sub_dict)
#    
#    return html_string
#         
#
#    
#class PerformanceMonitoringOptions(object):
#
#
#    def __init__(self):
#        """
#        A class to manage Performance Monitoring options
#        """
#        self.results_directory = 'results'
#        self.results_subdirectory_root = 'subdir'
#        self.results_subdirectory_prefix = '_prefix'
#        
#    def make_results_directory(self):       
#        """
#        Make results directory
#        """
#        if not os.path.exists(self.results_directory):
#            os.makedirs(self.results_directory)
#        
#    def make_results_subdirectory(self):
#        """
#        Make results subdirectory
#        """
#        self.results_subdirectory = os.path.join(self.results_directory, self.results_subdirectory_root + self.results_subdirectory_prefix)
#        
#        if not os.path.exists(self.results_subdirectory):
#            os.makedirs(self.results_subdirectory)
#        
#    def clean_results_subdirectory(self):
#        """
#        Clean results subdirectory.  This removes all files in pm.results_subdirectory
#        """
#        self.results_subdirectory = os.path.join(self.results_directory, self.results_subdirectory_root + self.results_subdirectory_prefix)
#        
#        for file_name in glob(os.path.join(self.results_subdirectory, '*')):
#            os.remove(file_name)
#        