
#include "transform.h"

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
