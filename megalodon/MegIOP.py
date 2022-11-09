import os
import rich_click as click
import netCDF4 as nc
import numpy as np
import random
import matplotlib as matplotlib
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import AutoMinorLocator
from matplotlib.ticker import FormatStrFormatter
from matplotlib.colors import BoundaryNorm
import matplotlib.patches as mpatches
from matplotlib.markers import MarkerStyle
import matplotlib.patheffects as PathEffects
from matplotlib.image import imread
import matplotlib.dates as mdates
import matplotlib.mlab as mlab
import matplotlib.cm as cm
import matplotlib.contour
import pandas as pd
import datetime as dt
from datetime import datetime
import time 
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.contour
import xarray as xr
import statistics
import csv
import metpy
from metpy.units import units, pandas_dataframe_to_unit_arrays
import metpy.calc as mpcalc
from metpy.plots import SkewT
from metpy.plots import ImagePlot, MapPanel, PanelContainer
from metpy.calc import wind_components
from metpy.interpolate import cross_section
from scipy.constants import convert_temperature

from . import MegContext
from .DotMap import SmartDict

class IopFile(MegContext.Base):
    @property
    def processed_datafile(self):
        if self._processed_datafile is None:
            self.processed_datafile = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'nevzorov_corr_IOP23.nc'))
        return self._processed_datafile
    @processed_datafile.setter
    def processed_datafile(self, value):
        self._processed_datafile=value

    @property
    def datafile(self):
        if self._datafile is None:
            self.datafile = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'data', '20170309b.c1.nc'))
        return self._datafile
    @datafile.setter
    def datafile(self, value):
        self._datafile=value

    def __init__(self, *args, **kwargs):
        super(IopFile, self).__init__(*args, **kwargs)
        self.data=nc.Dataset(self.processed_datafile, 'r')
        self.orig_data=nc.Dataset(self.datafile, 'r')
        self.datatime=self.data.variables['time_s'][:] #Dimension 14371, Units: hours since 1/1/1970
        # self.datatime=[datetime.utcfromtimestamp(t) for t in self.datatime]
        # self.datatime=self.datatime[0:int(len(self.datatime)/2)]
        self.lwc=self.data.variables['lwc_corr'][:] #units g/m^3
        # self.lwc=self.data.variables['lwc_raw'][:] #units g/m^3
        # self.lwc=self.lwc[0:int(len(self.lwc)/2)]
        self.iwc=self.data.variables['iwc_corr'][:] #units g/m^3
        # self.iwc=self.data.variables['iwc_raw'][:] #units g/m^3
        # self.iwc=self.iwc[0:int(len(self.iwc)/2)]
        self.twc=self.data.variables['twc_corr'][:] #units g/m^3
        # self.twc=self.data.variables['twc_raw'][:] #units g/m^3
        # self.twc=self.twc[0:int(len(self.twc)/2)]


        IOP23_Orig=self.orig_data
        # UWKA_Time =IOP23_Orig.variables['time'][:] #time dimensions 14371  #seconds since 1/1/2017 00:00:00  IOP12 time interval 19:30:25 - 23:29:55 2/7/2017 (1486495825 - 1486510195)
        # td =IOP23_Orig.variables['tdp'][:]  #dew point temp degrees Celsius
        # mr =IOP23_Orig.variables['mr'][:]  #mixing ratio g/kg
        # rh =IOP23_Orig.variables['rh'][:]  #relative humidity %
        # PALT =IOP23_Orig.variables['PALT'][:]  #Pressure altitude meters
        # alt =IOP23_Orig.variables['ztrue'][:] #hypsometric altitude meters
        # tas =IOP23_Orig.variables['tas'][:]  #true airspeed m/s
        # GLAT =IOP23_Orig.variables['GLAT'][:]  # latitude degrees north 
        # GLON =IOP23_Orig.variables['GLON'][:]  #Longitude degrees east
        # GALT =IOP23_Orig.variables['GALT'][:]  #Altitude meters
        # topo =IOP23_Orig.variables['topo'][:]  #topography meters WGS84 aster
        # pTemp =IOP23_Orig.variables['thetad'][:] # potential temperature dry K
        # eTemp =IOP23_Orig.variables['thetae'][:]  #Equivalent potential temperature K 
        # twodp =IOP23_Orig.variables['twodp'][:] # 2DP shadow or concentration liter-1 sample rate 10 
        # uwind =IOP23_Orig.variables['avuwind'][:] #horizontal wind e/w component (x axis) m/s
        # vwind =IOP23_Orig.variables['avvwind'][:]  # horizontal wind n/s component (yaxis) m/s
        # zwind =IOP23_Orig.variables['avwwind'][:]  #vertical wind up component (z axis) m/s upward air verlocity 
        # winddir =IOP23_Orig.variables['avwdir'][:]  #real time wind direction (from) degree T 
        # windmag =IOP23_Orig.variables['avwmag'][:]  #real time wind magnitude m/s
        # CDP_Con =IOP23_Orig.variables['cdpconc_NRB'][:] #DMT CDP Total Concentration (/cc)
        # CDP_LWC =IOP23_Orig.variables['cdplwc_NRB'][:]  #DMT CDP Liquid Water Content (g/m^3)
        # CDP_Diam =IOP23_Orig.variables['cdpdbar_NRB'][:] #DMT CDP Mean Diameter (um)
        # UWKA_Temp =IOP23_Orig.variables['trose'][:] #Temperature degrees celsius
        # UWKA_Time_IOP23 = UWKA_Time + 1483228800 #seconds from 1/1/1970 - 1/1/2017
        # UWKA_Time_Corr = mdates.epoch2num(UWKA_Time_IOP23)
        Micro_Time = mdates.epoch2num(self.datatime)
        _df=pd.DataFrame({'lwc':self.lwc, 'iwc':self.iwc, 'twc':self.twc, 'time':self.datatime})
        # _df=pd.DataFrame({'iwc':self.iwc, 'twc':self.twc, 'time':self.datatime})
        # _df['lwc'] = _df['twc'] - _df['iwc']
        _start=1489088733.0
        # _start=datetime(2017,3,9,20).timestamp()
        # _start=1489114800.0
        _stop= 1489089734.0
        _df=_df[_df['time']>_start]
        _df=_df[_df['time']<_stop]
        # _df=_df[_df['iwc']>-1]
        # _df=_df[_df['lwc']>-1]
        # _df=_df[_df['twc']>-1]
        # _df['lwc'] = _df['twc'] - _df['iwc']
        _df['time']=pd.to_datetime(_df['time'], unit='s')
        self.df=_df


    def __call__(self, *args, **kwargs):
        self.logger.info('Data:\n{}'.format(self.df))
        return self




@click.command('iop',context_settings=dict(help_option_names=['-h', '--help'], ignore_unknown_options=True))
@click.option('-d','--datafile',            default=None, help="Datafile to use")
@click.option('-p','--processed-datafile',  default=None, help="Processed Datafile to use")
@click.pass_context
def _iop(ctx, *args, **kwargs):
    opts = SmartDict({kk:None if vv in [tuple(), None] else vv for kk,vv in kwargs.items() }, dict(_context=ctx.obj()))
    iop=IopFile(**opts)()
    # df.show()

if __name__ == "__main__":
    _iop()