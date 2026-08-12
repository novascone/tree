
#ifndef TRANSFORM_H
#define TRANSFORM_H

#include <array>
#include <cmath> 
#include <string>

template <typename CoordSystem>
struct Transform;

struct Geographic {};

template <>
struct Transform<Geographic> {
   static constexpr double R_meters = 6371000;
   static const std::array<std::string, 3> axis_names;
   static std::array<double,3> to_cart(double lat, double lon, double alt);
   static std::array<double,3> from_cart(double x, double y, double z); 
};

template <typename VectorConvention>
struct Basis;

struct ENU {};

template <>
struct Basis<ENU> {
   static std::array<std::array<double,3>,3> local_basis(double x, double y, double z);
};

#endif
