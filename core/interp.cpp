
#include "interp.h"
#include <stdexcept>

TriInterp::TriInterp(Read& data, std::array<bool, 3> periodic_p) : loaded_data(data), periodic(periodic_p), saved_index{}, correlated{} {

   double lower_bound_0 = std::min(loaded_data.coords[0].front(), loaded_data.coords[0].back());
   double upper_bound_0 = std::max(loaded_data.coords[0].front(), loaded_data.coords[0].back());
   double span_0 = std::abs(loaded_data.coords[0].back() - loaded_data.coords[0].front());
   double cell_width_0 = span_0 / (loaded_data.coords[0].size() - 1);
   double period_0 = span_0 + cell_width_0;
   
   double lower_bound_1 = std::min(loaded_data.coords[1].front(), loaded_data.coords[1].back());
   double upper_bound_1 = std::max(loaded_data.coords[1].front(), loaded_data.coords[1].back());
   double span_1 = std::abs(loaded_data.coords[1].back() - loaded_data.coords[1].front());
   double cell_width_1 = span_1 / (loaded_data.coords[1].size() - 1);
   double period_1 = span_1 + cell_width_1;

   double lower_bound_2 = std::min(loaded_data.coords[2].front(), loaded_data.coords[2].back());
   double upper_bound_2 = std::max(loaded_data.coords[2].front(), loaded_data.coords[2].back()); 
   double span_2 = std::abs(loaded_data.coords[2].back() - loaded_data.coords[2].front());
   double cell_width_2 = span_2 / (loaded_data.coords[2].size() - 1);
   double period_2 = span_2 + cell_width_2;
   
   periods = {period_0, period_1, period_2};
      
   bounds[0] = std::make_pair(lower_bound_0, upper_bound_0);
   bounds[1] = std::make_pair(lower_bound_1, upper_bound_1);
   bounds[2] = std::make_pair(lower_bound_2, upper_bound_2);


   for (int i = 0; i < 3; i++) {
      hunt_threshold[i] = std::min(1, static_cast<int>(std::pow(static_cast<double>(loaded_data.coords[i].size()), 0.25)));
   }
}

int TriInterp::locate(int axis, const std::vector<double>& axis_line, double query) {
    
   int new_saved = Read::bisection(axis_line, query);
   correlated[axis] = (std::abs(saved_index[axis] - new_saved) <= hunt_threshold[axis]) ? 1 : 0;
   saved_index[axis] = new_saved;
   
   return saved_index[axis];
}

std::array<int, 2> TriInterp::hunting(int axis, const std::vector<double>& axis_line, double query) {

   int index_low = saved_index[axis]; 
   int index_high = saved_index[axis]; 
   int n = static_cast<int>(axis_line.size());
   int inc = 1;

   bool ascending = (axis_line[n-1] >= axis_line[index_low]) ? true : false;
   
   if (ascending) {
      if (query >= axis_line[index_low]){
         while (query >= axis_line[index_high]) { // hunt up
            index_high += inc;
            if (index_high > n-1) {
               index_high = n-1;
               break;
            }
            inc*=2;
         }
      }
      else {
         while (query <= axis_line[index_low]) { // hunt down
            index_low -= inc;
            if (index_low < 0) {
               index_low = 0;
               break;
            }
            inc*=2;
         } 
      }
   }
   else {
      if (query <= axis_line[index_low]){
         while (query <= axis_line[index_high]) { // hunt up
            index_high += inc;
            if (index_high > n-1) {
               index_high = n-1;
               break;
            }
            inc*=2;
         }
      }
      else {
         while (query >= axis_line[index_low]) { // hunt down
            index_low -= inc;
            if (index_low < 0) {
               index_low = 0;
               break;
            }
            inc*=2;
         } 
      }
   }
   return {index_low, index_high};
}

int TriInterp::hunt(int axis, const std::vector<double>& axis_line, double query) {

   std::array<int, 2> trophy = TriInterp::hunting(axis, axis_line, query);
   int new_saved = Read::bisection(axis_line, query, trophy[0], trophy[1]);
   correlated[axis] = (std::abs(saved_index[axis] - new_saved) <= hunt_threshold[axis]) ? 1 : 0;
   saved_index[axis] = new_saved; 
   
   return saved_index[axis]; 
}

std::vector<Neighbor> TriInterp::getNeighbors(std::array<double, 3>& position) { 
   
   for (int i = 0; i < 3; i++) {
      if (periodic[i]) {
         position[i] = bounds[i].first + std::fmod(position[i] - bounds[i].first + periods[i], periods[i]); 
      }
      if (position[i] < bounds[i].first || position[i] > bounds[i].second) {
         throw std::runtime_error("Position out of bounds");
      }
   }
   std::vector<Neighbor> neighbors;
   int neighbor_index_0 = correlated[0] ? hunt(0, loaded_data.coords[0], position[0]) : locate(0, loaded_data.coords[0], position[0]);
   int neighbor_index_1 = correlated[1] ? hunt(1, loaded_data.coords[1], position[1]) : locate(1, loaded_data.coords[1], position[1]);
   int neighbor_index_2 = correlated[2] ? hunt(2, loaded_data.coords[2], position[2]) : locate(2, loaded_data.coords[2], position[2]); 
   for (int i = 0; i <= 1; i++) {
      for (int j = 0; j <= 1; j++) {
         for (int k = 0; k <= 1; k++) {
            std::array<double, 3> coords {}; 
            coords[0] = loaded_data.coords[0][neighbor_index_0 + i];
            coords[1] = loaded_data.coords[1][neighbor_index_1 + j];
            coords[2] = loaded_data.coords[2][neighbor_index_2 + k];
            int index = Read::convertIDXFlat(neighbor_index_0 + i, neighbor_index_1 + j, neighbor_index_2 + k,
                                       static_cast<int>(loaded_data.coords[1].size()), static_cast<int>(loaded_data.coords[2].size()));
            std::vector<double> values;
            for ( const std::vector<double>& var : loaded_data.values) {
               values.push_back(var[index]);
            }
            Neighbor neighbor(coords, values);
            neighbors.push_back(neighbor);
         }
      }
   }
   return neighbors; 
}

std::vector<double> TriInterp::interp(std::array<double, 3> position) {

   double t {};
   double u {};
   double v {};

   int x_high_index = 4;
   int y_high_index = 2;
   int z_high_index = 1;
   int low_index = 0;

   std::vector<double> interp_value {};

   std::vector<Neighbor> neighbors = getNeighbors(position);

   interp_value.resize(neighbors[0].values.size());
   
   t = (position[0] - neighbors[0].coords[0]) / (neighbors[x_high_index].coords[0] - neighbors[low_index].coords[0]);   
   u = (position[1] - neighbors[0].coords[1]) / (neighbors[y_high_index].coords[1] - neighbors[low_index].coords[1]);
   v = (position[2] - neighbors[0].coords[2]) / (neighbors[z_high_index].coords[2] - neighbors[low_index].coords[2]);

   if (loaded_data.sentinel.has_value()) {  
      for (int i = 0; i < static_cast<int>(neighbors[0].values.size()); i++) {
         for (int j = 0; j < 8; j++) {
            if (neighbors[j].values[i] == loaded_data.sentinel) throw std::runtime_error("missing value in interpolation neighbor");
         }
      }

   }
   
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


