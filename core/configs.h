
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
   
   struct VecRenderConfig {

      std::string colormap;
      std::string line_type;
      int seed_count;
      std::string seed_distribution;
 
   };

   struct ScalarRenderConfig {
      
      std::string colormap;

   };

   std::optional<VecRenderConfig> vec_render;
   std::optional<ScalarRenderConfig> scalar_render;


};

struct TREEConfig {

   GeometryConfig geometry;
   std::vector<FieldConfig> fields;
   
};

#endif
