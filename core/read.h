
#ifndef READ_H
#define READ_H

#include "configs.h"
#include <hdf5.h>
#include <vector>
#include <array>

struct NetCDFFile {
   
   const int file_id;

   NetCDFFile(const std::string& file_path,  int NCFlag);
   ~NetCDFFile();
};

struct HDF5File {
   const hid_t file_id;

   HDF5File(const std::string& file_path);
   ~HDF5File();
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
   static std::vector<double> readHDF5Variable(hid_t, const std::string& name);
      
   public:
   const std::vector<std::vector<double>> coords;
   const std::vector<std::vector<double>> values;
   const std::optional<double> sentinel;
   Read();
   Read(std::vector<std::vector<double>> coords, std::vector<std::vector<double>> values);
   Read(const FieldConfig& field_config_p); 
   static int openNetCDF(const std::string& file_path,  int NCFlag);
   static hid_t openHDF5File(const std::string& file_path);
   static std::vector<std::vector<double>> loadValues(const FieldConfig& field_config_p, const std::vector<std::vector<double>>& coords);
   static std::vector<std::vector<double>> loadCoords(const FieldConfig& field_config_p);
   static void reorder_coords(const FieldConfig& field_config,  std::vector<std::vector<double>>& coords);
   static void reorder_values(const FieldConfig& field_config, const std::vector<std::vector<double>>& coords, std::vector<std::vector<double>>& values);
   static void loadNetCDFValues(const FieldConfig& field_config, const std::vector<std::vector<double>>& coords,  std::vector<std::vector<double>>& values);
   static void loadNetCDFCoords(const FieldConfig& field_config,  std::vector<std::vector<double>>& coords);
   static void loadHDF5Values(const FieldConfig& field_config, const std::vector<std::vector<double>>& coords, std::vector<std::vector<double>>& values);
   static void loadHDF5Coords(const FieldConfig& field_config, std::vector<std::vector<double>>& coords);
   static int bisection(const std::vector<double>& axis_coords, double query, int index_low = 0, int index_high = -1);
   static int convertIDXFlat(int index0, int index1, int index2, int dim1, int dim2);

};


#endif
