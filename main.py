#!/usr/bin/env python
import netCDF4
from pybrain.datasets import SupervisedDataSet

def main():

  # Input consists of the NDVI of the square surrounding a point, and the point 
  #   itself, over the prior year's worth of observations (9 data points times 
  #   3 data sets times twelve months), the value of the current month in hours, 
  #   and the latitude and longitude of the point.

  # Output is the NDVI of the point.
  ds = SupervisedDataSet( ((9*3)*12) + 1 + 2, 1 )

  veg_data = get_ncdf_data('ndviavhrr19812001.nc')
  prec_data = get_ncdf_data('precipud19002008.nc')
  temp_data = get_ncdf_data('sfctempud19002008.nc')

  # Precipitation and temperature data start in January 1901, while vegetation
  #   data begins in July 1991.
  offset = 12*91 + 6
  
  for year in range(1, 13, 3):  # Train on every third year, to avoid any 
                                # intersection with test data at all
    for month in range(0, 12):
      m = 12*year + month

def get_ncdf_data(filename):
  f = netCDF4.Dataset(filename, 'r');
  return f.variables['data']
 
if __name__ == "__main__":
  main()

