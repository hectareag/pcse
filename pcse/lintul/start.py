# -*- coding: utf-8 -*-
import yaml

from ..base_classes import MultiCropParameterProvider, ParameterProvider
from ..engine import Engine
from ..fileinput.cabo_weather import CABOWeatherDataProvider
from ..fileinput import PCSEFileReader
from datetime import date
import lintul3parameters
from ..lintul.lintul3 import SubModel
from numbers import Number
import os


class Lintul3Model(Engine):

    

    @classmethod
    def readModelParameters(cls, module):
        '''
        read model parameters from a slightly (syntax) adapted Model.dat
        :param module: an imported module
        '''
        allvars = module.__dict__
        params = dict((k, v) for k, v in allvars.items() if  not k.startswith('_'))
        return params        


    @classmethod
    def start(cls, year=1997, outputProc = None):
        
        t = """
            Version: 1.0
            AgroManagement:
            - {start_date}:
                CropCalendar:
                    crop_id: spring-wheat
                    crop_start_date: {crop_start_date}
                    crop_start_type: emergence
                    crop_end_date: {crop_end_date}
                    crop_end_type: earliest
                    max_duration: 366
                TimedEvents: 
                -   event_signal: apply_n
                    name:  Nitrogen application table
                    comment: All nitrogen amounts in g N m-2
                    events_table:
                    - {year}-04-10: {{amount: 10, recovery: 0.7}}
                    - {year}-05-05: {{amount:  5, recovery: 0.7}}
                StateEvents: null
        """

        t = t.format(year=year,
                     start_date=date(year, 01, 01), 
                     crop_start_date=date(year, 03, 31),
                     crop_end_date=date(year, 10, 20))#, end_date=date(year, 12, 31))
        
        agromanagement = yaml.load(t)['AgroManagement']
        dirname = r"D:\UserData\sources\pcse\pcse\pcse\tests\test_data"
        soil = PCSEFileReader(os.path.join(dirname, "lintul3_parameters.soil"))
        crop = {"spring-wheat": PCSEFileReader(os.path.join(dirname, "lintul3_parameters.crop"))}
        parameterprovider   = MultiCropParameterProvider(sitedata={}, soildata=soil,
                                                         multi_cropdata=crop, init_root_depth_name="ROOTDI",
                                                         max_root_depth_name="ROOTDM")
        weatherdataprovider = CABOWeatherDataProvider("NL1", dirname, ETmodel="PM")
    
        SubModel.onOutput   = outputProc    
        return Lintul3Model(parameterprovider, weatherdataprovider, agromanagement=agromanagement, 
                            config="lintul3.conf.py")

    

if (__name__ == "__main__"):
    
    class P:            
        __lineBuffer = {}
        __headerBuffer = {}
        __headerPrinted = False


        def printRow(self, values):
            for v in values:
                if isinstance(v, Number):
                    print "%f\t" % (v),
                else:
                    print "%s\t" % (v),
            print
            
            
        def __call__(self, values, header = None):
            if header:
                self.printRow(header)
            self.printRow(values)


        
    p = P()
    
    sim = Lintul3Model.start(1987, outputProc=p)
    
    sim.run(365)
    SubModel.doOutput(sim.crop, 99999, {})
    print "END STOP ENDJOB "*5

    