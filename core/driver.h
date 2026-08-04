
#ifndef DRIVER_H
#define DRIVER_H

#include "read.h"
#include "interp.h"
#include <cmath>

using Streamline = std::vector<std::vector<double>>;
using StreamlineSet = std::vector<Streamline>;

struct Derivative {
   
   TriInterp& interp;
   const std::optional<std::vector<std::string>>& variable_directions; 
   const double PI = 3.14159265358979323846;

   std::vector<char> sign_chars;
   std::vector<std::string> axis_names;
   std::vector<double> signs;
   std::array<int, 3> perm;
   std::vector<std::string> standard = {"lat", "lon", "alt"};
   double R_meters = 6371000;



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
       
      std::vector<double> arbitrary = interp.interp({position[0], position[1], position[2]});
      std::fill(derivative.begin(), derivative.end(), 0.0);
      for (int i = 0; i < 3; i++) {
         if (perm[i] != -1) {
            if (i == 0) 
               derivative[i] = signs[perm[i]] * arbitrary[perm[i]] / R_meters;
            else if (i == 1)
               derivative[i] = signs[perm[i]] * arbitrary[perm[i]] / (R_meters * std::cos(position[0]));
            else
               derivative[i] = signs[perm[i]] * arbitrary[perm[i]];
         }
      }      
   } 
};

StreamlineSet driveField(Read& loaded_data, std::vector<std::vector<double>>& seeds, double interval_start, double interval_end, double initial_step_size);

#endif
