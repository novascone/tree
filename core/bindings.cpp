
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include "configs.h"
#include "mesh.h"
#include "build_mesh.h"
#include "driver.h"
#include "interp.h"

namespace py = pybind11;

PYBIND11_MAKE_OPAQUE(std::vector<FieldConfig>);
PYBIND11_MAKE_OPAQUE(std::vector<std::string>);

PYBIND11_MODULE(tree_core, m) {
   m.doc() = "TREE core module";
   m.def("build_mesh", &buildMesh); 
   m.def("driveField", &driveField); 
 
   py::bind_vector<std::vector<FieldConfig>>(m, "FieldConfigList");
   py::bind_vector<std::vector<std::string>>(m, "StringVector"); 

   py::class_<GeometryConfig>(m, "GeometryConfig")
      .def(py::init<>())
      .def_readwrite("name", &GeometryConfig::name)
      .def_readwrite("type", &GeometryConfig::type)
      .def_readwrite("source", &GeometryConfig::source)
      .def_readwrite("parameters", &GeometryConfig::parameters);

   py::class_<FieldConfig>(m, "FieldConfig")
      .def(py::init<>())
      .def_readwrite("name", &FieldConfig::name)
      .def_property("type",[](FieldConfig field_config) {
                              if (field_config.type == FieldType::vec) {
                                 return "vector";
                              }
                              else if (field_config.type == FieldType::scalar) {
                                 return "scalar";
                              }
                              else {
                                 throw field_config.type; 
                              }
                           },
                           [](FieldConfig &field_config, std::string type) {
                              if (type == "vector") {
                                 field_config.type = FieldType::vec;
                              }
                              else if (type == "scalar") {
                                 field_config.type = FieldType::scalar;
                              }
                              else {
                                 throw type;
                              }
                           } 
                  )           
      .def_readwrite("source", &FieldConfig::source)
      .def_readwrite("grid_type", &FieldConfig::grid_type)
      .def_readwrite("variables", &FieldConfig::variables)
      .def_readwrite("coordinates", &FieldConfig::coordinates)
      .def_readwrite("coord_order", &FieldConfig::coord_order)
      .def_readwrite("coordinate_system", &FieldConfig::coordinate_system)
      .def_readwrite("altitude", &FieldConfig::altitude);
    
   py::class_<TREEConfig>(m, "TREEConfig")
      .def(py::init<>())
      .def_readwrite("geometry", &TREEConfig::geometry)
      .def_readwrite("fields" , &TREEConfig::fields);

   py::class_<Mesh>(m, "Mesh")
      .def(py::init<>())
      .def_readwrite("name", &Mesh::name)
      .def_readwrite("positions", &Mesh::positions)
      .def_readwrite("faces", &Mesh::faces);

   py::class_<Neighbor>(m, "Neighbor")
      .def_readonly("coords", &Neighbor::coords)
      .def_readonly("values", &Neighbor::values);

   py::class_<Read>(m, "Read")
      .def(py::init<FieldConfig>()) 
      .def_readonly("coords", &Read::coords)
      .def_readonly("values", &Read::values);

   py::class_<TriInterp>(m, "TriInterp")
      .def(py::init<Read&>())
      .def("interp", &TriInterp::interp);
}
   

