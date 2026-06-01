
#ifndef DRIVER_H
#define DRIVER_H

#include "read.h"
#include "interp.h"

using Streamline = std::vector<std::vector<double>>;
using StreamlineSet = std::vector<Streamline>;

struct Derivative {
   
   TriInterp& interp;

   Derivative(TriInterp& t) : interp(t) {}

   void operator()(const double, std::vector<double>& y, std::vector<double>& dydx) {
      
      std::vector<double> arbitrary = interp.interp({y[0], y[1], y[2]});

      dydx[0] = arbitrary[0];
      dydx[1] = arbitrary[1];
      dydx[2] = arbitrary[2];
   }
};

Read load(FieldConfig field_config);

StreamlineSet driveField(Read& loaded_data, std::vector<std::vector<double>>& seeds, double interval_start, double interval_end, double initial_step_size);

#endif
