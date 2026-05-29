
#include "interp.h"

TriInterp::TriInterp(Read& data) : loaded_data(data) {}

std::vector<double> TriInterp::interp(std::array<double, 3> position) {

   double t {};
   double u {};
   double v {};

   std::vector<double> interp_value {};

   std::vector<Neighbor> neighbors = loaded_data.getNeighbors(position);

   interp_value.resize(neighbors[0].values.size());
   
   t = (position[0] - neighbors[0].coords[0]) / (neighbors[4].coords[0] - neighbors[0].coords[0]);   
   u = (position[1] - neighbors[0].coords[1]) / (neighbors[2].coords[1] - neighbors[0].coords[1]);
   v = (position[2] - neighbors[0].coords[2]) / (neighbors[1].coords[2] - neighbors[0].coords[2]);
   
   for (int i = 0; i < static_cast<int>(neighbors[0].values.size()); i++) {
      interp_value[i] = (1-t) * (1-u) * (1-v) * neighbors[0].values[i]
                      + (1-t) * (1-u) *    v  * neighbors[1].values[i]
                      + (1-t) *    u  * (1-v) * neighbors[2].values[i]
                      + (1-t) *    u  *    v  * neighbors[3].values[i]
                      +    t  * (1-u) * (1-v) * neighbors[4].values[i]
                      +    t  * (1-u) *    v  * neighbors[5].values[i]
                      +    t  *    u  * (1-v) * neighbors[6].values[i]
                      +    t  *    u  *    v  * neighbors[7].values[i];
   }

   return interp_value;
}


