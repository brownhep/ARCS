""" An example of an alibava plugin
    This example implements a user defined scan. The idea is
    that we want to make a laser scan across all the strips in 
    the sensor, take a fixed number of events on each position and
    save only the data of the neighbouring channels
"""

import time
import inspect
import struct
import alibava
from cStringIO import StringIO

#
# Define some usefull constants
# 
# Block types
NewFile,StartOfRun, DataBlock, CheckPoint, EndOfRun = range(0,5)

# Run types
Unknown,Calibration,LaserSync,Laser,RadSource,Pedestal,LastRType = range(0,7)

#
# We define here a series of classes that tell when we should
# move to the next scan point
#
class NewPoint(object):
    """ This class tells when a new scan point is needed
    """
    def __init__(self):
        """ Initialization
        """
        self.started = False
        
    def check(self, ievt):
        """ Returns True when we should change the scan point
        """
        return False
    
    def reset(self):
        """ Resets the state
        """ 
        pass
    
    def next(self):
        """ Increments the state
        """ 
        pass
    
    def start(self):
        """ Starts
        """
        self.started = True
        pass
    
class EventCounter(NewPoint):
    """ This one know how many events per scan point we
        want. 
    """
    def __init__(self, nevts):
        super(EventCounter, self).__init__()
        self.nevts = nevts
        self.cntr = 0
        
    def check(self, ievt):
        if (ievt - self.cntr) >= self.nevts:
            self.cntr = ievt
            return True
        else:
            return False
        
    def reset(self):
        self.cntr = 0
        
    def start(self):
        super(EventCounter, self).start()
        self.cntr = 0

class EventTimer(NewPoint):
    """ This one will make each scan point last the
        same time. This is useful when trying different
        parameters with a radioactive source.
    """
    def __init__(self, time_step):
        """ Accepts as argument the duration in 
            seconds
        """
        super(EventTimer, self).__init__()
        self.time_step = time_step
        self.time = 0.
    
    def start(self):
        super(EventCounter, self).start()
        self.time = time.clock()
        
    def reset(self):
        self.time = time.clock()
        
    def check(self, ievt):
        if time.clock() - self.time > self.time_step:
            self.time = time.clock()
            return True
        else:
            return False
        
class MyPlugin(object):
    """ This is an object that can be loaded by alibava to
        be called at certain stages of the DAQ process.
        
    """
    def __init__(self):
        """ Initialization 
        """
        self.current_point = 0
        self.current_event = 0
        self.npoints = 50            # number of scan points
        self.nevt_per_point = 1000   # number of events per point
        self.handler = EventCounter(self.nevt_per_point)
        self.run_type = -1
        
    def new_file(self):
        """ This is called at the beginning of each file
            It should return a string with information 
            that will be stored in the file header
        """
        print "new_file"
        return "%d %d %d" % ( self.current_point, self.npoints, self.nevt_per_point )
    
    def start_of_run(self, run_type, nevts):
        """ This is called at the beginning of each run. 
            run_type: the run type. Run types are predefined in the variables:
                       Unknown,Calibration,LaserSync,Laser,RadSource,Pedestal
            nevts - total number of events for this run
                          
            It should return the total number of events that we want to acquire. 
            
        """
        info_msg("Starting a new run")
        daq = alibava.DAQConfig()
        self.handler.start()
        self.run_type = run_type
        write_msg( "start_of_run %d events. Run type: %d" % (nevts, run_type ) )
        write_msg( "...sample size %d" % (daq.sample_size) )
        if run_type == Pedestal:
            return nevts
        
        self.handler.reset()
        daq.sample_size = self.handler.nevts
        write_msg("Changing sample size to %d" % (daq.sample_size))
        self.nevt_per_point = daq.sample_size
            
        if run_type!= RadSource and run_type!=Laser:
            return nevts
        else:
            # Here we return the number of events we really
            # want to acquire given that we need to scan npoints
            # with nevt_per_point events per point.
            return self.npoints * self.nevt_per_point
    
    def end_of_run(self):
        """ Called at the end of a run
        """
        write_msg("pyplugin: end_of_run")
        return "end_of_run"
    
    def new_event(self, ievt):
        """ This is called at the beginning of each event.
            Should return True if we want alibava to call 
            the method new_point.
            
            The input parameter is the current event number
        """
        self.current_event = ievt
        if self.handler.check(ievt):
            return True
        else:
            return False
    
    def move_axis(self):
        """ A dummy function where we could, for instance,
            move the axis that hole the laser or the source
        """
        pass
    
    def new_point(self):
        """ Called every time that new_event returns True
        """
        if self.run_type == Pedestal:
            return ""
        
        self.current_point += 1
        self.move_axis()
        print "new_point %d event %d" % (self.current_point, self.current_event)
        return "Current axis position is %d" % self.current_point
    
    def filter_event(self, time, temp, value, data):
        """ This function allows you to change the information that
            is written on disk for the DataBlock. The arguments are:
                time: the TDC time
                temp: the temperature measured at the daughter board
                value: the value of the current quantity being scanned
                data: It is a sequence like ( chip1, chip2 ) where
                        chip = ( header, data)
                        and header is a sequence with the 16 header values
                        and data is a sequence with the 128 channel values
                
            It should return a string object with the data to be stored in
            the DataBlock
            
            In this example we just return the channel hit by the laser plus the
            neighbours.
        """
        bfr   = StringIO()
        ana = alibava.Analysis()
        hits = ana.hits
        if len(hits) == 0:
            return ""
            
        i1 = hits[0][0] - 2
        ichip = i1/128
        if ichip<0:
            ichip = 0
            
        i1 = i1 % 128
        if i1<0:
            i1 = 0
        
        i2 = i1 + 5
        if i2 > 128:
            i1 = 123
            i2 = 128
            
        print hits[0],'[',i1,',',i2,']'
        # we will only save channels around current point
        for ichan in range(i1, i2):
            bfr.write( struct.pack("2H", 128*ichip+ichan, data[ichip][1][ichan]) )
            
        out = bfr.getvalue()
        bfr.close()
        return out
        
        
def create_plugin():
    """ This is the 'hook'. This is the method called to
        create an instance of the MyPlugin class
    """
    write_msg("Loading %s" % __name__)
    plugin = MyPlugin()
    return plugin