#!/usr/bin/env python
import netCDF4
import numpy as np
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.structure.modules import SigmoidLayer
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.validation import ModuleValidator

def main():
  train, val = getData()

  net = buildNetwork(39, 25, 1, hiddenclass=SigmoidLayer, outclass=SigmoidLayer)
  trainer = BackpropTrainer(net, train)

  train_errs = []
  val_errs = []

  for i in range(1000):
    terr = trainer.train()
    train_errs.append(terr)
    verr = ModuleValidator.MSE(net, val)
    val_errs.append(verr)
    print verr, terr

  return  (train_errs, val_errs)



def getData():
  # Input consists of the NDVI of a point, over the prior year's worth of 
  #   3-month-spaced observations (1 data point times 3 data sets times 4
  #   months), the value of the current month, and the latitude and longitude of 
  #   the point.

  # Output is the NDVI of the point.
  train = SupervisedDataSet( 3*12 + 1 + 2, 1 )
  val = SupervisedDataSet( 3*12 + 1 + 2, 1 )

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
    for month in range(0, 12, 3):
      t = int(12*year + month)

      for start_lat, start_lon, ds in [(10, 0, train), (15, 5, val)]:
        for lat in range(start_lat, lats, 10):
          for lon in range(start_lon, lons, 10):
            s = available_point(veg_data, prec_data, temp_data, lat, lon, t, offset)
            if s != None:
              ds.addSample((list(s.ravel()) + [t % 12, lat, lon]),
                            (veg_data[t,lat,lon]))
  return (train, val)

def get_ncdf_data(filename):
  f = netCDF4.Dataset(filename, 'r');
  return f.variables['data']

def available_point(ndvi, prec, temp, lat, lon, t, offset):
  result = [ndvi[range(t-12, t), lat, lon],
    prec[range(t-12+offset, t+offset), lat*2-1, lon*2],
    temp[range(t-12+offset, t+offset), lat*2, lon*2]]

  # Determine whether the specified data point is acceptable.
  for set in result:
    if type(set) != np.ndarray or set.shape[0] != 12:
      return None

  return np.array(result)
 
if __name__ == "__main__":
  main()

