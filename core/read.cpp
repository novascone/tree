
#include "read.h"
#include <netcdf.h>
#include <filesystem>
#include <vector>
#include <algorithm>
#include <cmath>
#include <stdexcept>

NetCDFFile::NetCDFFile(const std::string& file_path, int NCFlag) {
   
   int status = nc_open(file_path.c_str(), NCFlag, &file_id);
   
   if (status != NC_NOERR) throw std::runtime_error(nc_strerror(status));
   
}

NetCDFFile::~NetCDFFile() {
   
   nc_close(file_id);
}

Read::Read(){}

Read::Read(FieldConfig field_config) { 
   std::filesystem::path p(field_config.source);
   if (p.extension() == ".nc") {
 
      NetCDFFile netcdf_file(field_config.source, NC_NOWRITE);

      if (field_config.variables.has_value()) {
         for (const std::string& name : field_config.variables.value()) {  
            values.push_back(readNetCDFVariable(netcdf_file.file_id, name));
         }
      }

      if (field_config.coordinates.has_value()) {
         int i = 0;
         for (const std::string& name : field_config.coordinates.value()) {
            coords.push_back(readNetCDFVariable(netcdf_file.file_id, name));
            hunt_threshold[i] = std::min(1, static_cast<int>(std::pow(static_cast<double>(coords[i].size()), 0.25)));
            saved_index[i] = 0;
            correlated[i] = 0; 
            i++;
         } 
      } 
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

int Read::locate(int axis, const std::vector<double>& axis_line, double query) {
    
   int new_saved = Read::bisection(axis_line, query);
   correlated[axis] = (std::abs(saved_index[axis] - new_saved) <= hunt_threshold[axis]) ? 1 : 0;
   saved_index[axis] = new_saved;
   
   return saved_index[axis];
}

std::array<int, 2> Read::hunting(int axis, const std::vector<double>& axis_line, double query) {

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

int Read::hunt(int axis, const std::vector<double>& axis_line, double query) {

   std::array<int, 2> trophy = hunting(axis, axis_line, query);
   int new_saved = bisection(axis_line, query, trophy[0], trophy[1]);
   correlated[axis] = (std::abs(saved_index[axis] - new_saved) <= hunt_threshold[axis]) ? 1 : 0;
   saved_index[axis] = new_saved; 
   
   return saved_index[axis]; 
}


int Read::convertIDXFlat(int index0, int index1, int index2, int dim1, int dim2) { 
   return index0 * (dim1 * dim2) + index1 * dim2 + index2;
}

std::vector<Neighbor> Read::getNeighbors(std::array<double, 3> position) {

   std::vector<Neighbor> neighbors;
   int neighbor_index_0 = correlated[0] ? hunt(0, coords[0], position[0]) : locate(0, coords[0], position[0]);
   int neighbor_index_1 = correlated[1] ? hunt(1, coords[1], position[1]) : locate(1, coords[1], position[1]);
   int neighbor_index_2 = correlated[2] ? hunt(2, coords[2], position[2]) : locate(2, coords[2], position[2]); 
   for (int i = 0; i <= 1; i++) {
      for (int j = 0; j <= 1; j++) {
         for (int k = 0; k <= 1; k++) {
            Neighbor neighbor;
            neighbor.coords[0] = coords[0][neighbor_index_0 + i];
            neighbor.coords[1] = coords[1][neighbor_index_1 + j];
            neighbor.coords[2] = coords[2][neighbor_index_2 + k];
            int index = convertIDXFlat(neighbor_index_0 + i, neighbor_index_1 + j, neighbor_index_2 + k,
                                       static_cast<int>(coords[1].size()), static_cast<int>(coords[2].size()));
            for ( const std::vector<double>& var : values) {
               neighbor.values.push_back(var[index]);
            }
            neighbors.push_back(neighbor);
         }
      }
   }
   return neighbors; 
}

