#!/usr/bin/env python
import netCDF4
import numpy as np
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
  #   data begins in 1991.
  offset = 12*91
  
  lats, lons = veg_data[0,:,:].shape

  # This is currently too slow. It may be better if we only pay attention to the
  # particular point in question (limiting dimensionality to 12 + 2 + 1)

  for year in np.arange(1.5, 13, 3):  # Train on every third year, to avoid any 
                                      # intersection with test data at all
    for month in range(0, 12):
      t = int(12*year + month)
      for lat in range(10, lats):
        for lon in range(lons):
          s = is_available_point(veg_data, prec_data, temp_data, lat, lon, t, offset)
          if s != None:
            print t, lat, lon
            ds.addSample((list(s.ravel()) + [t % 12, lat, lon]), 
                          (veg_data[t,lat,lon],))
        print "nextlat"
  return ds


      #input = (veg_data[])

      #ds.addSample(input)

def get_ncdf_data(filename):
  f = netCDF4.Dataset(filename, 'r');
  return f.variables['data']

def is_available_point(ndvi, prec, temp, lat, lon, t, offset):
  # Determine whether the specified data point is acceptable.
  t = int(t)
  lat = int(lat)
  lon = int(lon)
  offset = int(offset)
  result = [ndvi[range(t-12, t), 
    [lat-1, lat, lat+1], 
    [lon-1, lon, lon+1]],
     
    prec[range(t-12+offset, t+offset), 
      [(lat-1)*2, lat*2, (lat+1)*2], 
      [(lon-1)*2, lon*2, (lon+1)*2]],
    
    temp[range(t-12+offset, t+offset), 
      [(lat-1)*2, lat*2, (lat+1)*2], 
      [(lon-1)*2, lon*2, (lon+1)*2]]]

  for set in result:
    s = set.shape
    if type(set) != np.ndarray or s[0] != 12 or s[1] != 3 or s[2] != 3:
      return None

  return np.array(result)
 
if __name__ == "__main__":
  main()

