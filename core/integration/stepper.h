
#ifndef STEPPER_H
#define STEPPER_H

#include<vector>

struct Stepper {
   
   double& interval_position;
   double interval_position_old;
   std::vector<double>& values;
   std::vector<double>& derivatives;
   int num_equations {};  
   std::vector<double> value_errors;
   std::vector<double> value_outputs;
   bool hermite_out {};
   double absolute_error {};
   double relative_error {};
   double taken_step {};
   double next_step {};
   double mach_eps {};
   

   Stepper(double& interval_position_p, std::vector<double>& values_p, std::vector<double>& derivatives_p,
           double absolute_error_p, double relative_error_p, bool hermite_out_p) : 
           interval_position(interval_position_p), values(values_p), derivatives(derivatives_p),
           num_equations(static_cast<int>(values_p.size())), value_errors(num_equations),
           value_outputs(num_equations), hermite_out(hermite_out_p), absolute_error(absolute_error_p),
           relative_error(relative_error_p) {} 
   
};
   
#endif
