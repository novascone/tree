
#include "interp.h"

TriInterp::TriInterp(Read& data) : loaded_data(data) {}

std::vector<double> TriInterp::interp(std::array<double, 3> position) {

   double t {};
   double u {};
   double v {};

   int x_high_index = 4;
   int y_high_index = 2;
   int z_high_index = 1;
   int low_index = 0;

   std::vector<double> interp_value {};

   std::vector<Neighbor> neighbors = loaded_data.getNeighbors(position);

   interp_value.resize(neighbors[0].values.size());
   
   t = (position[0] - neighbors[0].coords[0]) / (neighbors[x_high_index].coords[0] - neighbors[low_index].coords[0]);   
   u = (position[1] - neighbors[0].coords[1]) / (neighbors[y_high_index].coords[1] - neighbors[low_index].coords[1]);
   v = (position[2] - neighbors[0].coords[2]) / (neighbors[z_high_index].coords[2] - neighbors[low_index].coords[2]);
   
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


