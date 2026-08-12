
#include "transform.h"

const std::array<std::string, 3> Transform<Geographic>::axis_names = {"lat", "lon", "alt"};

std::array<double,3> Transform<Geographic>::to_cart(double lat, double lon, double alt) {

   double r = R_meters + alt;
   double x = r * cos(lat) * cos(lon);
   double y = r * cos(lat) * sin(lon);
   double z = r * sin(lat);

   std::array<double,3> xyz = {x, y, z};

   return xyz;
}

std::array<double,3> Transform<Geographic>::from_cart(double x, double y, double z) {

   double r = sqrt(x*x + y*y + z*z);
   double lat = asin(z/r);
   double lon = atan2(y, x);
   double alt = r - R_meters;

   std::array<double,3> lla = {lat, lon, alt};

   return lla;
}

std::array<std::array<double,3>,3> Basis<ENU>::local_basis(double x, double y, double z) {

   std::array<std::array<double,3>,3> basis {};
   std::array<double,3> up {};
   std::array<double,3> east {};
   std::array<double,3> north {};


   double mag = sqrt(x*x + y*y + z*z);
   x = x/mag;
   y = y/mag;
   z = z/mag;
   
   up = {x, y, z};

   double east_mag = sqrt(x*x + y*y);
   east = {-y/east_mag, x/east_mag, 0};
   
   north = {-(x*z)/east_mag, -(y*z)/east_mag, (x*x + y*y)/east_mag};

   basis = {north, east, up};
   
   return basis;

}
