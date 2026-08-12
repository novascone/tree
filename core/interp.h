
#ifndef INTERP_H
#define INTERP_H

#include <array>
#include <cmath>
#include "read.h"

struct TriInterp {

   Read& loaded_data;
   std::array<bool,3> periodic;
   std::array<int, 3> hunt_threshold;
   std::array<int, 3> saved_index; 
   std::array<int, 3> correlated; 
   std::array<std::pair<double, double>, 3> bounds;
   std::array<double,3> periods {};
   TriInterp(Read& data, const std::array<bool,3> periodic);
   int locate(int axis, const std::vector<double>& axis_line, double query);
   std::array<int, 2> hunting(int axis, const std::vector<double>& axis_line, double query); 
   int hunt(int axis, const std::vector<double>& axis_line, double query);
   std::vector<Neighbor> getNeighbors(std::array<double, 3>& position);
   std::vector<double> interp(std::array<double, 3> position); 
};



#endif
