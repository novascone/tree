
#include <catch2/catch_test_macros.hpp>
#include <catch2/catch_approx.hpp>
#include "driver.h"
#include <cmath>

TEST_CASE("Adaptive Runge-Kutta 5th order circular flow test") {
   
   std::vector<std::vector<double>> coords = {{-2.0, -1.0, 0.0, 1.0, 2.0}, {-2.0, -1.0, 0.0, 1.0, 2.0}, {0.0, 1.0}};
   std::vector<std::vector<double>> values;
   values.resize(3);
   for (int i = 0; i < 5; i++) {
      for (int j = 0; j < 5; j++) {
         for (int k = 0; k < 2; k++) {
            values[0].push_back(-coords[1][j]);
            values[1].push_back(coords[0][i]);
            values[2].push_back(0.0);
         }
      }
   }

   Read read(coords, values);

   
   
   std::vector<std::vector<double>> seeds = {{{1.0, 0.0, 0.0}}}; 

   StreamlineSet results = driveField(read, seeds, 0.0, M_PI*2, 0.1);

REQUIRE(results[0].back()[0] == Catch::Approx(1.0));


}

