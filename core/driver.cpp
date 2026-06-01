
#include "driver.h"
#include "adaptiverk5.h"
#include "integrator.h"

Read load(FieldConfig field_config) {
   Read data(field_config);
   return data;
}

StreamlineSet driveField(Read& loaded_data, std::vector<std::vector<double>>& seeds, double interval_start,
                         double interval_end, double initial_step_size) {

   StreamlineSet results(static_cast<int>(seeds.size()));
   TriInterp triInterp(loaded_data); 
   Derivative derivative(triInterp);
   int i = 0;
   for (std::vector<double> query : seeds) {
      Output out(0); 
      Integrator<AdaptiveRK5<Derivative>> integrator(query, interval_start, interval_end, 1.0e-10, 1.0e-10, initial_step_size,
                                                     1.0e-12, out, derivative);
      integrator.integrate(); 
      for (int j = 0; j < out.count; j++) {
         results[i].push_back({out.values_saved[j][0], out.values_saved[j][1], out.values_saved[j][2]});
      }
      i++;
   }

   return results;
}
