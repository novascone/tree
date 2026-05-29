
#ifndef READ_H
#define READ_H

#include "configs.h"
#include <vector>
#include <array>

struct Neighbor {

   public:
   std::array<double, 3> coords;
   std::vector<double> values; 

};

class Read {

   private:
   std::array<int, 3> hunt_threshold;
   std::array<int, 3> saved_index; 
   std::vector<double> readNetCDFVariable(int file_id, const std::string& name); 
   int convertIDXFlat(int index0, int index1, int index2, int dim1, int dim2);
   
   public:
   std::vector<std::vector<double>> coords;
   std::vector<std::vector<double>> values; 
   std::array<int, 3> correlated;
   Read();
   Read(FieldConfig field_config);
   std::vector<Neighbor> getNeighbors(std::array<double, 3> position);
   int bisection(const std::vector<double>& axis_coords, double query, int index_low = 0, int index_high = -1);
   int locate(int axis, const std::vector<double>& axis_coords, double query);
   std::array<int, 2> hunting(int axis, const std::vector<double>& axis_coords, double query);
   int hunt(int axis, const std::vector<double>& axis_coords, double query);
};


#endif
