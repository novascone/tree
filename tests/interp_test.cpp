
#include <catch2/catch_test_macros.hpp>
#include <catch2/catch_approx.hpp>
#include "interp.h"
#include "read.h"

TEST_CASE("TriLinear interp test") {
   
   Read read;
   read.coords = {{0.0, 1.0}, {0.0, 1.0}, {0.0, 1.0}};
   read.values = {{0, 0, 0, 0, 1, 1, 1, 1}}; 

   TriInterp tri_interp(read);

   std::vector<double> result = tri_interp.interp({0.5, 0.5, 0.5});
   
   REQUIRE(result[0] == Catch::Approx(0.5));
}


