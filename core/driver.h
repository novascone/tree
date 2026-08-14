
#ifndef DRIVER_H
#define DRIVER_H

#include "read.h"
#include "interp.h"
#include "transform.h"
#include "adaptiverk5.h"
#include "integrator.h"
#include "query.h"
#include <omp.h>
#include <cmath>

using Streamline = std::vector<std::vector<double>>;
using StreamlineSet = std::vector<Streamline>;

template <typename CoordSystem, typename VectorConvention>

struct Derivative {
   
   TriInterp& interp;
   const std::optional<std::vector<std::string>>& variable_directions; 
   const double PI = 3.14159265358979323846;

   std::vector<char> sign_chars;
   std::vector<std::string> axis_names;
   std::vector<double> signs;
   std::array<int, 3> perm;
   const std::array<std::string,3> standard = Transform<CoordSystem>::axis_names;



   Derivative(TriInterp& t, const std::optional<std::vector<std::string>>& variable_directions_p) : interp(t), variable_directions(variable_directions_p)  {

      
      sign_chars.resize((*variable_directions).size());
      axis_names.resize(sign_chars.size()); 
      signs.resize(axis_names.size());
      std::fill(perm.begin(), perm.end(), -1);

      for (int i = 0; i < static_cast<int>((*variable_directions).size()); i++) {
         sign_chars[i] = ((*variable_directions)[i][0]);
         axis_names[i] = ((*variable_directions)[i].substr(1));
         signs[i] = ((sign_chars[i] == '-') ? -1.0 : 1.0);
      }
          
      for (int i = 0; i < 3; i++) {
         for (int j = 0; j < static_cast<int>((*variable_directions).size()); j++) {
            if (standard[i] == axis_names[j])
               perm[i] = j;
         }
      } 
   }

   void operator()(const double, std::vector<double>& position, std::vector<double>& derivative) {
      std::array<double,3> native_pos = Transform<CoordSystem>::fromCart(position[0], position[1], position[2]); 
      std::array<std::array<double,3>,3> current_basis = Basis<VectorConvention>::localBasis(position[0], position[1], position[2]);
      std::vector<double> arbitrary = interp.interp({native_pos[0], native_pos[1], native_pos[2]});
      std::fill(derivative.begin(), derivative.end(), 0.0);
      for (int i = 0; i < 3; i++) {
         if (perm[i] != -1) {
            for (int j = 0; j < 3; j++) {
               derivative[j] += signs[perm[i]] * arbitrary[perm[i]] * current_basis[i][j];
            }
         }
      }      
   } 
};

template <typename CoordSystem, typename VectorConvention>

StreamlineSet driveField(Read& loaded_data, std::vector<std::vector<double>>& seeds, double interval_start,
                         double interval_end, double initial_step_size) {

   double default_absolute_error = 1.0e-10;
   double default_relative_error = 1.0e-10;
   double default_min_step_size = 1.0e-12; 
   
   std::array<bool,3> periodic = getPeriodic<CoordSystem>(loaded_data);

   StreamlineSet results(static_cast<int>(seeds.size()));
   #pragma omp parallel for 
   for (int i = 0; i < static_cast<int>(seeds.size()); i++) {
      TriInterp triInterp(loaded_data, periodic); 
      Derivative<CoordSystem, VectorConvention> derivative(triInterp, loaded_data.variable_directions); 

      try {
         Output out(0); 
         Integrator<AdaptiveRK5<Derivative<CoordSystem, VectorConvention>>> integrator(seeds[i], interval_start, interval_end, default_absolute_error, default_relative_error, initial_step_size,
                                                        default_min_step_size, out, derivative);
         integrator.integrate(); 
         for (int j = 0; j < out.count; j++) {
            results[i].push_back({out.values_saved[j][0], out.values_saved[j][1], out.values_saved[j][2]});
         }
      }
      catch (const std::exception&) {}
   }

   return results;
}
#endif
