
#include "adaptiverk5.h"
#include "integrator.h"
#include <iostream>
#include <cmath>

// compile commmands
// g++ -std=c++17 -I core -I core/integration -I $CONDA_PREFIX/include tests/adaptiverk5_test.cpp core/read.cpp core/interp.cpp -L
//  $CONDA_PREFIX/lib -lnetcdf -o tests/adaptiverk5
//  LD_LIBRARY_PATH=$CONDA_PREFIX/lib ./tests/adaptiverk5

void deriv(const double x, std::vector<double>& y, std::vector<double>& dydx) {

   dydx[0] = y[0];
}

int main() {

   std::vector<double> y;
   y.push_back({1.0});
   std::vector<double> dydx(1);
   Output out(1); 
   deriv(0.0, y, dydx);
   
   Integrator<AdaptiveRK5<decltype(deriv)>> my_ode(y, 0.0, 1.0, 1.0e-10, 1.0e-10, 0.1, 1.0e-12, out, deriv);
   try {
     my_ode.integrate();
   } catch (const char* e) {
      std::cerr << e << std::endl;
   }   
   std::cout << out.values_saved[1][0] << std::endl;
   std::cout << std::exp(1.0) << std::endl;
}
