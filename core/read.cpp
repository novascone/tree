
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

HDF5File::HDF5File(const std::string& file_path): file_id(Read::openHDF5File(file_path)) {}

HDF5File::~HDF5File() {

   H5Fclose(file_id);
}

hid_t Read::openHDF5File(const std::string& file_path) {
   hid_t file_id = H5Fopen(file_path.c_str(), H5F_ACC_RDONLY, H5P_DEFAULT);
   if (file_id < 0) throw std::runtime_error("Failed to open HDF5 file: " + file_path);
   return file_id;
}

Read::Read(){}

Read::Read(std::vector<std::vector<double>> coords_p, std::vector<std::vector<double>> values_p): coords(coords_p), values(values_p) {}

Read::Read(const FieldConfig& field_config_p): coords(loadCoords(field_config_p)), values(loadValues(field_config_p, coords)) {}

std::vector<std::vector<double>> Read::loadCoords(const FieldConfig& field_config_p) {
   std::filesystem::path p(field_config_p.source); 
   std::vector<std::vector<double>> coords; 

   if (p.extension() == ".nc") {
      Read::loadNetCDFCoords(field_config_p, coords);
      return coords;
   }
   if (p.extension() == ".h5" || p.extension() == ".hdf5") {
      Read::loadHDF5Coords(field_config_p, coords);
      return coords;
   }
   throw std::runtime_error("Unsupported file format: " + p.extension().string());
}

std::vector<std::vector<double>> Read::loadValues(const FieldConfig& field_config_p, const std::vector<std::vector<double>>& coords) {
   std::filesystem::path p(field_config_p.source); 
   std::vector<std::vector<double>> values;

   if (p.extension() == ".nc") {
      Read::loadNetCDFValues(field_config_p, coords, values);
      return values;
   }
   if (p.extension() == ".h5" || p.extension() == ".hdf5") {
      Read::loadHDF5Values(field_config_p, coords, values);
      return values;
   }
   throw std::runtime_error("Unsupported file format: " + p.extension().string());
}

void Read::loadNetCDFValues(const FieldConfig& field_config, const std::vector<std::vector<double>>& coords, std::vector<std::vector<double>>& values) { 
 
   NetCDFFile netcdf_file(field_config.source, NC_NOWRITE);    

   if (field_config.variables.has_value()) {
      for (const std::string& name : field_config.variables.value()) {  
         values.push_back(readNetCDFVariable(netcdf_file.file_id, name));
      }
   if (field_config.coord_order.has_value()) {
      Read::reorder_values(field_config, coords, values);
   }
   }  
}

void Read::loadNetCDFCoords(const FieldConfig& field_config, std::vector<std::vector<double>> &coords) {   
   
   NetCDFFile netcdf_file(field_config.source, NC_NOWRITE);  

   if (field_config.coordinates.has_value()) {
      for (const std::string& name : field_config.coordinates.value()) {
         coords.push_back(readNetCDFVariable(netcdf_file.file_id, name)); 
      }
   if (field_config.coord_order.has_value()) {
      Read::reorder_coords(field_config, coords) ;
   }
   } 
}

void Read::loadHDF5Values(const FieldConfig &field_config, const std::vector<std::vector<double>>& coords, std::vector<std::vector<double>> &values) {
   HDF5File hdf5_file(field_config.source);
   if (field_config.variables.has_value()) {
      for (const std::string& name : field_config.variables.value()) {
         values.push_back(readHDF5Variable(hdf5_file.file_id, name));
      }
   }
   if (field_config.coord_order.has_value()) {
      Read::reorder_values(field_config, coords, values);
   }
}

void Read::loadHDF5Coords(const FieldConfig &field_config, std::vector<std::vector<double>> &coords) {
   HDF5File hdf5_file(field_config.source);
   if (field_config.coordinates.has_value()) {
      for (const std::string& name : field_config.coordinates.value()) {
         coords.push_back(readHDF5Variable(hdf5_file.file_id, name));
      }
   if (field_config.coord_order.has_value()) {
      Read::reorder_coords(field_config, coords) ;
   }
   }
}

void Read::reorder_coords(const FieldConfig &field_config, std::vector<std::vector<double>> &coords) {
   std::array<int, 3> perm;
   std::vector<std::string> standard = {"lat", "lon", "alt"};
   std::vector<std::vector<double>> reorder;
   std::vector<std::string> coord_order = field_config.coord_order.value();
   for (int i = 0; i < 3; i++) {
      for (int j = 0; j < 3; j++) {
         if (standard[i] == coord_order[j])
            perm[i] = j;
      }
   }
   for (int i = 0; i < 3; i++) {
      for (int j = 0; j < 3; j++) {
         if (perm[i] == j) {
            reorder.push_back(coords[j]);
         }
      }
   }
   coords = reorder;
}

void Read::reorder_values(const FieldConfig &field_config, const std::vector<std::vector<double>> &coords, std::vector<std::vector<double>> &values) {
   std::array<int, 3> perm;
   std::array<int, 3> inv_perm;
   std::vector<std::string> standard = {"lat", "lon", "alt"}; 
   std::vector<double> new_buffer; 
   int n0 = coords[0].size();
   int n1 = coords[1].size();
   int n2 = coords[2].size();
   new_buffer.resize(n0 * n1 * n2);
   std::vector<std::string> coord_order = field_config.coord_order.value();
   for (int i = 0; i < 3; i++) {
      for (int j = 0; j < 3; j++) {
         if (standard[i] == coord_order[j])
            perm[i] = j;
      }
   }
   for (int i = 0; i < 3; i++) {
      for (int j = 0; j < 3; j++) {
         if (perm[i] == j) {
            inv_perm[j] = i; 
         }
      }
   }

   for (int v = 0; v < static_cast<int>(values.size()); v++) {
      for (int i = 0; i < n0; i++) {
         for (int j = 0; j < n1; j++) {
            for (int k = 0; k < n2; k ++) {
               std::array<int, 3> idx{i, j, k};
               int new_idx = convertIDXFlat(i, j, k, n1, n2);
               int old_idx = convertIDXFlat(idx[inv_perm[0]], idx[inv_perm[1]], idx[inv_perm[2]], coords[inv_perm[1]].size(), coords[inv_perm[2]].size());  
               new_buffer[new_idx] = values[v][old_idx];
            }
         }
      }
   values[v] = new_buffer;
   }
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

std::vector<double> Read::readHDF5Variable(hid_t file_id, const std::string& name) {

   hid_t dataset_id = H5Dopen2(file_id, name.c_str(), H5P_DEFAULT);
   if (dataset_id < 0) throw std::runtime_error("Failed to open dataset: " + name);

   hid_t space_id = H5Dget_space(dataset_id);
   hssize_t total = H5Sget_simple_extent_npoints(space_id);

   std::vector<double> buffer(total);
   H5Dread(dataset_id, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, buffer.data());
   H5Sclose(space_id);
   H5Dclose(dataset_id);

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


