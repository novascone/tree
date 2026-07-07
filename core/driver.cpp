
#include "driver.h"
#include "adaptiverk5.h"
#include "integrator.h"
#include <omp.h>

StreamlineSet driveField(Read& loaded_data, std::vector<std::vector<double>>& seeds, double interval_start,
                         double interval_end, double initial_step_size) {

   double default_absolute_error = 1.0e-10;
   double default_relative_error = 1.0e-10;
   double default_min_step_size = 1.0e-12;

   double lower_bound_0 = std::min(loaded_data.coords[0].front(), loaded_data.coords[0].back());
   double upper_bound_0 = std::max(loaded_data.coords[0].front(), loaded_data.coords[0].back());
   
   double lower_bound_1 = std::min(loaded_data.coords[1].front(), loaded_data.coords[1].back());
   double upper_bound_1 = std::max(loaded_data.coords[1].front(), loaded_data.coords[1].back());

   double lower_bound_2 = std::min(loaded_data.coords[2].front(), loaded_data.coords[2].back());
   double upper_bound_2 = std::max(loaded_data.coords[2].front(), loaded_data.coords[2].back());

   std::array<std::pair<double, double>, 3> bounds {};
      
   bounds[0] = std::make_pair(lower_bound_0, upper_bound_0);
   bounds[1] = std::make_pair(lower_bound_1, upper_bound_1);
   bounds[2] = std::make_pair(lower_bound_2, upper_bound_2);

   StreamlineSet results(static_cast<int>(seeds.size()));
   #pragma omp parallel for 
   for (int i = 0; i < static_cast<int>(seeds.size()); i++) {
      TriInterp triInterp(loaded_data); 
      Derivative derivative(triInterp, true); 

      try {
         Output out(0); 
         Integrator<AdaptiveRK5<Derivative>> integrator(seeds[i], interval_start, interval_end, default_absolute_error, default_relative_error, initial_step_size,
                                                        default_min_step_size, out, derivative);
         integrator.integrate(bounds, true); 
         for (int j = 0; j < out.count; j++) {
            results[i].push_back({out.values_saved[j][0], out.values_saved[j][1], out.values_saved[j][2]});
         }
      }
      catch (const std::exception&) {}
   }

   return results;
}
