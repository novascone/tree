
#ifndef MESH_H
#define MESH_H

#include <string>
#include <vector>

struct Mesh {

   std::string name;
   std::vector<double> positions;
   std::vector<int> faces;

   };

#endif 

