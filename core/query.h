
#ifndef QUERY_H
#define QUERY_H

#include "interp.h"
#include "transform.h"
#include <cmath>

template <typename CoordSystem>

std::array<bool,3> getPeriodic(Read& loaded_data) {
   std::array<bool, 3> periodic {};
  if (loaded_data.periodic.has_value()) {
     for (int i = 0; i < 3; i++) {
        for (int j = 0; j < static_cast<int>((*loaded_data.periodic).size()); j++) {
           if (Transform<CoordSystem>::axis_names[i] == (*loaded_data.periodic)[j])
              periodic[i] = true;
        }
     }
  }

   return periodic;
}

template <typename CoordSystem>

std::vector<double> getMags(Read& loaded_data, std::vector<std::array<double,3>> positions) {
   TriInterp interp(loaded_data, getPeriodic<CoordSystem>(loaded_data));
   std::vector<double> mags {};

   for (std::array<double,3> position : positions) { 
      std::array<double,3> native_pos = Transform<CoordSystem>::fromCart(position[0], position[1], position[2]);

      try {
      std::vector<double> interp_vector = interp.interp({native_pos[0], native_pos[1], native_pos[2]});
      double collapse {};
      for (int i = 0; i < static_cast<int>(interp_vector.size()); i++) {
         collapse += interp_vector[i] * interp_vector[i]; 
      }
      mags.push_back(sqrt(collapse));
      }
      catch(const std::exception&) {
         mags.push_back(0.0);
      }
   }

   return mags;
}

#endif


