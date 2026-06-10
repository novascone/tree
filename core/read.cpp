
#include "read.h"
#include <netcdf.h>
#include <filesystem>
#include <vector>
#include <cmath>
#include <stdexcept>

NetCDFFile::NetCDFFile(const std::string& file_path, int NCFlag): file_id(Read::openNetCDF(file_path, NCFlag)) {}
   
NetCDFFile::~NetCDFFile() {
   
   nc_close(file_id);
}

int Read::openNetCDF(const std::string& file_path, int NCFlag) {

   int file_id;
   int status = nc_open(file_path.c_str(), NCFlag, &file_id);
   
   if (status != NC_NOERR) throw std::runtime_error(nc_strerror(status));

   return file_id;
}

Read::Read(){}

Read::Read(std::vector<std::vector<double>> coords_p, std::vector<std::vector<double>> values_p): coords(coords_p), values(values_p) {}

Read::Read(const FieldConfig& field_config_p): coords(loadNetCDFCoords(field_config_p)), values(loadNetCDFValues(field_config_p)) {}

std::vector<std::vector<double>> Read::loadNetCDFValues(const FieldConfig& field_config) {
   std::filesystem::path p(field_config.source);
   std::vector<std::vector<double>> NetCDF_values;
   if (p.extension() == ".nc") {
 
      NetCDFFile netcdf_file(field_config.source, NC_NOWRITE);    

      if (field_config.variables.has_value()) {
         for (const std::string& name : field_config.variables.value()) {  
            NetCDF_values.push_back(readNetCDFVariable(netcdf_file.file_id, name));
         }
      } 
   }
   return NetCDF_values;
}

std::vector<std::vector<double>> Read::loadNetCDFCoords(const FieldConfig& field_config) {
   std::filesystem::path p(field_config.source);
   std::vector<std::vector<double>> NetCDF_coords;
   if (p.extension() == ".nc") { 
      NetCDFFile netcdf_file(field_config.source, NC_NOWRITE);  

      if (field_config.coordinates.has_value()) {
         for (const std::string& name : field_config.coordinates.value()) {
            NetCDF_coords.push_back(readNetCDFVariable(netcdf_file.file_id, name)); 
         } 
      } 
   }
   return NetCDF_coords;
}

std::vector<double> Read::readNetCDFVariable(int file_id, const std::string& name) {
   int var_id;
   int status = nc_inq_varid(file_id, name.c_str(), &var_id); 

   if (status != NC_NOERR) throw std::runtime_error(nc_strerror(status));
 
   int ndims;
   int dim_ids[NC_MAX_VAR_DIMS];
   status = nc_inq_var(file_id, var_id, nullptr, nullptr, &ndims, dim_ids, nullptr);

   if (status != NC_NOERR) throw std::runtime_error(nc_strerror(status));
  
   size_t total = 1;
   for (int i = 0; i < ndims; i++) {
      size_t len;
      status = nc_inq_dimlen(file_id, dim_ids[i], &len);

      if (status != NC_NOERR) throw std::runtime_error(nc_strerror(status));

      total *= len;
   } 
   std::vector<double> buffer(total);
   status = nc_get_var_double(file_id, var_id, buffer.data());

   if (status != NC_NOERR) throw std::runtime_error(nc_strerror(status));

   return buffer; 
}

int Read::bisection(const std::vector<double>& axis_line, double query, int index_low, int index_high) {

   int n = static_cast<int>(axis_line.size());
   int index_middle {};
   if (index_high == -1) index_high = n-1;
 
   bool ascending = (axis_line[index_high] - axis_line[index_low] >= 0) ? true : false;
    
   while (index_high - index_low > 1) {
      if (ascending) { 
         index_middle = ((index_high + index_low) / 2);
         if (query >= axis_line[index_middle]) index_low = index_middle;
         else index_high = index_middle;
      }
      else {
         index_middle = ((index_high + index_low) / 2);
         if (query <= axis_line[index_middle]) index_high = index_middle;
         else index_low = index_middle;  
      }
   }
   return index_low;
}

int Read::convertIDXFlat(int index0, int index1, int index2, int dim1, int dim2) { 
   return index0 * (dim1 * dim2) + index1 * dim2 + index2;
}


