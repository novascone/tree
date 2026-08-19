
#ifndef TRANSFORM_H
#define TRANSFORM_H

#include <array>
#include <cmath> 
#include <string>
#include <map>
#include <stdexcept>

template <typename CoordSystem>
struct Transform;

struct Geographic {};

template <>
struct Transform<Geographic> { 
   static const std::array<std::string, 3> axis_names;
   static std::array<double,3> toCart(double lat, double lon, double alt, const std::map<std::string, double>& geometric_parameters);
   static std::array<double,3> fromCart(double x, double y, double z, const std::map<std::string, double>& geometric_parameters); 
};

struct Cartesian {};

template<>
struct Transform<Cartesian> {
   static const std::array<std::string, 3> axis_names;
   static std::array<double,3> toCart(double x, double y, double z, const std::map<std::string, double>& geometric_parameters);
   static std::array<double,3> fromCart(double x, double y, double z, const std::map<std::string, double>& geometric_parameters); 

};

template <typename VectorConvention>
struct Basis;

struct ENU {};

template <>
struct Basis<ENU> {
   static std::array<std::array<double,3>,3> localBasis(double x, double y, double z);
};

struct Standard {};

template<>
struct Basis<Standard> {
   static std::array<std::array<double,3>,3> localBasis(double, double, double);
};


#endif
