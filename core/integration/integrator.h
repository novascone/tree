
#ifndef INTEGRATOR_H
#define INTEGRATOR_H

#include <vector>
#include <limits>
#include <cmath>
#include <stdexcept>

#include "output.h"

template <class Stepper>
struct Integrator {

   static const int MAXSTP=50000;
   double mach_eps {}; 
   int num_equations {}; 
   std::vector<double> pos; 
   std::vector<double> derivative; 
   std::vector<double> start_pos;
   int num_successful {}; 
   int num_unsuccessful {};
   double interval_pos {}; 
   double interval_start {}; 
   double interval_end {}; 
   double min_step {}; 
   bool hermite_out; 
   Output& out;
   typename Stepper::Dtype& derivative_func; 
   Stepper stepper; 
   int num_steps {}; 
   double step {}; 

   Integrator(std::vector<double>& start_pos_p, const double interval_start_p, const double interval_end_p,
              const double absolute_error, const double relative_error, const double step_p,
              const double min_step_p, Output& out_p, typename Stepper::Dtype& derivative_func_p);

   void integrate();

};

template <class Stepper>
Integrator<Stepper>::Integrator(std::vector<double>& start_pos_p, const double interval_start_p,
                                const double interval_end_p, const double absolute_error,
                                const double relative_error, const double step_p, const double min_step_p,
                                Output& out_p, typename Stepper::Dtype& derivative_func_p) : 
                                num_equations(static_cast<int>(start_pos_p.size())), pos(num_equations),
                                derivative(num_equations), start_pos(start_pos_p), num_successful(0),
                                num_unsuccessful(0), interval_pos(interval_start_p), interval_start(interval_start_p),
                                interval_end(interval_end_p), min_step(min_step_p), hermite_out(out_p.hermite_out),
                                out(out_p), derivative_func(derivative_func_p),
                                stepper(interval_pos, pos, derivative, absolute_error, relative_error, hermite_out) {

   mach_eps = std::numeric_limits<double>::epsilon();
   step = (interval_end - interval_start > 0 ? std::abs(step_p) : -std::abs(step_p));
   for (int i = 0; i < num_equations; i ++) pos[i] = start_pos_p[i];
   out.init(stepper.num_equations, interval_start, interval_end);
}

template <class Stepper>
void Integrator<Stepper>::integrate() {

   derivative_func(interval_pos, pos, derivative);

   if(hermite_out) out.out(-1, interval_pos, pos, stepper, step);
   else out.save(interval_pos, pos);

   for (num_steps = 0; num_steps < MAXSTP; num_steps++) {
      // floating point loss of precision check 
      if ((interval_pos + step * 1.0001 - interval_end) * (interval_end - interval_start) > 0.0) {
         step = interval_end - interval_pos; 
      }

      stepper.step(step, derivative_func);
      if (stepper.taken_step == step) ++num_successful; else ++num_unsuccessful;
      if (hermite_out) out.out(num_steps, interval_pos, pos, stepper, stepper.taken_step);
      else out.save(interval_pos, pos);
      if ((interval_pos - interval_end) * (interval_end - interval_start) >= 0.0) { // done?
         for ( int i = 0; i < num_equations; i++) start_pos[i] = pos[i];
         // duplicate check
         if (out.capacity > 0 &&
             std::abs(out.interval_saved[out.count-1] - interval_end) > 100.0 * std::abs(interval_end) * mach_eps) {
            out.save(interval_pos, pos);
         }
         return; 
      }

      if (std::abs(stepper.next_step) <= min_step) throw std::runtime_error("Step too small in Integrator");
      step = stepper.next_step;
   }
   
   throw std::runtime_error("Too many steps in routine Integrator");
}   

#endif 
