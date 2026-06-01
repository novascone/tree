
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
      std::fill(dydx.begin(), dydx.end(), 0.0);

      for (int i = 0; i < static_cast<int>(arbitrary.size()); i++) {
         dydx[i] = arbitrary[i]; 
      }
   }
};

StreamlineSet driveField(Read& loaded_data, std::vector<std::vector<double>>& seeds, double interval_start, double interval_end, double initial_step_size);

#endif
