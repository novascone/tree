
#ifndef READ_H
#define READ_H

#include "configs.h"
#include <vector>
#include <array>

struct NetCDFFile {
   
   int file_id;

   NetCDFFile(const std::string& file_path,  int NCFlag);
   ~NetCDFFile();
};

struct Neighbor {

   public:
   std::array<double, 3> coords;
   std::vector<double> values; 

};

class Read {

   private: 
   std::vector<double> readNetCDFVariable(int file_id, const std::string& name); 
      
   public:
   std::vector<std::vector<double>> coords;
   std::vector<std::vector<double>> values;  
   Read();
   Read(FieldConfig field_config); 
   int bisection(const std::vector<double>& axis_coords, double query, int index_low = 0, int index_high = -1);
   int convertIDXFlat(int index0, int index1, int index2, int dim1, int dim2);

};


#endif
