
#ifndef CONFIGS_H
#define CONFIGS_H

#include <string>
#include <vector>
#include <optional>
#include <map>

enum class FieldType {scalar, vec};

struct GeometryConfig {

   std::string name;
   std::string type;
   std::optional<std::string> source;
   std::map<std::string, std::string> parameters;
   
};

struct FieldConfig {

   std::string name;
   FieldType type;
   std::string source;
   std::string grid_type;
   std::string coordinate_system;
   std::optional<std::vector<std::string>> variables;
   std::optional<std::vector<std::string>> coordinates;
   std::optional<std::vector<std::string>> coord_order;
   std::optional<double> altitude;
};

struct TREEConfig {

   GeometryConfig geometry;
   std::vector<FieldConfig> fields;
   
};

#endif
