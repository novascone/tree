
#ifndef READ_H
#define READ_H

#include "configs.h"
#include <vector>
#include <array>

struct NetCDFFile {
   
   const int file_id;

   NetCDFFile(const std::string& file_path,  int NCFlag);
   ~NetCDFFile();
};

struct Neighbor {

   public:
   const std::array<double, 3> coords;
   const std::vector<double> values; 

   Neighbor(std::array<double, 3> coords_p, std::vector<double> values_p) : coords(coords_p), values(values_p) {} ;

};

class Read {

   private: 
   static std::vector<double> readNetCDFVariable(int file_id, const std::string& name); 
      
   public:
   const std::vector<std::vector<double>> coords;
   const std::vector<std::vector<double>> values;  
   Read();
   Read(std::vector<std::vector<double>> coords, std::vector<std::vector<double>> values);
   Read(const FieldConfig& field_config_p); 
   static int openNetCDF(const std::string& file_path,  int NCFlag);
   static std::vector<std::vector<double>> loadNetCDFValues(const FieldConfig& field_config);
   static std::vector<std::vector<double>> loadNetCDFCoords(const FieldConfig& field_config);
   static int bisection(const std::vector<double>& axis_coords, double query, int index_low = 0, int index_high = -1);
   static int convertIDXFlat(int index0, int index1, int index2, int dim1, int dim2);

};


#endif
