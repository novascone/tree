
#ifndef DRIVER_H
#define DRIVER_H

#include "read.h"
#include "interp.h"
#include <cmath>

using Streamline = std::vector<std::vector<double>>;
using StreamlineSet = std::vector<Streamline>;

struct Derivative {
   
   TriInterp& interp;
   bool geographic {};
   const double PI = 3.14159265358979323846;

   Derivative(TriInterp& t, bool geographic_p = false) : interp(t), geographic(geographic_p) {}

   void operator()(const double, std::vector<double>& position, std::vector<double>& derivative) {
      
      std::vector<double> arbitrary = interp.interp({position[0], position[1], position[2]});
      std::fill(derivative.begin(), derivative.end(), 0.0);
      if (geographic) {
         double R_meters = 6371000;
         double lat_con = R_meters * PI / 180;
         double lat = position[0] * PI / 180;
         double lon_con = R_meters * std::cos(lat) * PI / 180;
         for (int i = 0; i < static_cast<int>(arbitrary.size()); i++) { 
            if ( i == 0) derivative[i] = arbitrary[i] / lat_con; 
            if ( i == 1) derivative[i] = arbitrary[i] / lon_con;
            if ( i == 2) derivative[i] = arbitrary[i];
         }
      }
      else {
         for (int i = 0; i < static_cast<int>(arbitrary.size()); i++) derivative[i] = arbitrary[i]; 
      }
   }
};

StreamlineSet driveField(Read& loaded_data, std::vector<std::vector<double>>& seeds, double interval_start, double interval_end, double initial_step_size);

#endif
