
#include "build_mesh.h"
#include "configs.h"
#include "mesh.h"
#include <stdexcept>
#include <string>
#include <cmath>

const double PI = 3.14159265358979323846;

namespace {
   Mesh buildSphere(std::string name, std::map<std::string, std::string> parameters) { 
      double rho = std::stod(parameters["radius"]);
      double resolution = std::stod(parameters["resolution"]);
   
      Mesh sphere;
      sphere.name = name;
      int rows = resolution;
      int cols = resolution;
      sphere.positions.resize((rows + 1) * (cols + 1) * 3);
      sphere.faces.resize(rows * cols * 4);
   
      for (int i = 0; i <= rows; i++) {
         for (int j = 0; j <= cols; j++) {
            double phi = j * ((2*PI)/cols);
            double theta = i * (PI/rows);
            sphere.positions[(i * (cols + 1) + j) * 3] = rho*std::sin(theta)*std::cos(phi);
            sphere.positions[(i * (cols + 1) + j) * 3 + 1] = rho*std::sin(theta)*std::sin(phi);
            sphere.positions[(i * (cols + 1) + j) * 3 + 2] = rho*std::cos(theta);
   
         }
      }
   
      for (int i = 0; i <= rows - 1; i++) {
         for(int j = 0; j <= cols - 1; j++) {
            sphere.faces[(i * cols + j) * 4] = i * (cols + 1) + j;
            sphere.faces[(i * cols + j) * 4 + 1] = (i + 1) * (cols + 1) + j;
            sphere.faces[(i * cols + j) * 4 + 2] = i * (cols + 1) + j + 1;
            sphere.faces[(i * cols + j) * 4 + 3] = (i + 1) * (cols + 1) + j + 1;
         }
      }
   
      return sphere;
   
   }
}

Mesh buildMesh(GeometryConfig config) {
   Mesh mesh;
   if (!config.source) {
      // Load mesh from file  
   }
   else {
      
      if (config.type == "sphere") {
        mesh = buildSphere(config.name, config.parameters);
      }
      else {
         throw std::invalid_argument("Unknown geometry type: " + config.type); 
      }
   }
   return mesh;
}






