
#ifndef ADAPTIVERK5_H
#define ADAPTIVERK5_H

#include "stepper.h"
#include <algorithm>
#include <limits>
#include <cmath>
#include <vector>

template <class D>
struct AdaptiveRK5 : Stepper { // Dormand-Prince 5th order Runge-Kutta step monitoring local truncation

   typedef D Dtype;
   std::vector<double> k1;
   std::vector<double> k2;
   std::vector<double> k3;
   std::vector<double> k4;
   std::vector<double> k5;
   std::vector<double> k6;
   std::vector<double> k7;
   std::vector<double> hermite1;
   std::vector<double> hermite2;
   std::vector<double> hermite3;
   std::vector<double> hermite4;
   std::vector<double> hermite5;
 
   AdaptiveRK5(double& interval_position_p, std::vector<double>& values_p, std::vector<double>& derivatives_p,
               const double absolute_error_p, const double relative_error_p, bool hermite_out_p);  

   void step(const double try_step, D& derivative); 
   void rungeKutta(const double step, D& derivative);
   void hermite(const double step, D&);
   std::vector<double> hermiteOut(const double interval_position, const double step);
   double error();

   struct Controller {
      
      double next_step {};
      bool reject {};
      double err_old {};
      
      Controller();

      bool success(const double err, double& step);
   };
   
   Controller controller;
};

template <class D>
AdaptiveRK5<D>::AdaptiveRK5(double& interval_position_p, std::vector<double>& values_p,
                                  std::vector<double>& derivatives_p, const double absolute_error_p,
                                  const double relative_error_p, bool hermite_out_p):
                                  Stepper(interval_position_p, values_p, derivatives_p,
                                          absolute_error_p, relative_error_p, hermite_out_p),
                                  k1(num_equations), k2(num_equations), k3(num_equations), k4(num_equations),
                                  k5(num_equations), k6(num_equations), k7(num_equations),
                                  hermite1(num_equations), hermite2(num_equations), hermite3(num_equations),
                                  hermite4(num_equations), hermite5(num_equations) {

   mach_eps = std::numeric_limits<double>::epsilon();
}

template <class D>
void AdaptiveRK5<D>::step(const double try_step, D& derivative) {

   double step = try_step;
   rungeKutta(step, derivative); 
   double err = error();
      
   while (!controller.success(err, step)) {
      if (interval_position == 0.0 && std::abs(step) <= mach_eps) throw("step too small"); 
      else if (std::abs(step / interval_position)  <= mach_eps) throw("step too small");
      rungeKutta(step, derivative);
      err = error();
   }
   
   if (hermite_out) hermite(step, derivative);
   
   derivatives = k7;
   values = value_outputs;
   interval_position_old = interval_position;
   interval_position += step;
   taken_step = step;
   next_step = controller.next_step;
    
}

template <class D>
void AdaptiveRK5<D>::rungeKutta(const double step, D& derivative) {

   k1 = derivatives;
   std::vector<double> temp_values(num_equations);
   for (int i = 0; i < num_equations; i++) temp_values[i] = values[i] + step * (1.0/5.0 * k1[i]);
   derivative(interval_position + 1.0/5.0 * step, temp_values, k2);
   for (int i = 0; i < num_equations; i++) temp_values[i] = values[i] + step * (3.0/40.0 * k1[i] + 9.0/40.0 * k2[i]);
   derivative(interval_position + 3.0/10.0 * step, temp_values, k3);
   for (int i = 0; i < num_equations; i++) temp_values[i] = values[i] + step * (44.0/45.0 * k1[i]  - 56.0/15.0 * k2[i] +
                                                                               32.0/9.0  * k3[i]);
   derivative(interval_position + 4.0/5.0 * step, temp_values, k4);
   for (int i = 0; i < num_equations; i++) temp_values[i] = values[i] + step * (19372.0/6561.0 * k1[i] - 25360.0/2187.0 *
                                                                                 k2[i] + 64448.0/6561.0 * k3[i] - 
                                                                                 212.0/729.0 * k4[i]);
   derivative(interval_position + 8.0/9.0 * step, temp_values, k5);
   for (int i = 0; i < num_equations; i++) temp_values[i] = values[i] + step * (9017.0/3168.0 * k1[i] - 355.0/33.0 *
                                                                                k2[i] + 46732.0/5247.0 * k3[i] +
                                                                                49.0/176.0 * k4[i] - 5103.0/18656.0 *
                                                                                k5[i]);
   derivative(interval_position + 1 * step, temp_values, k6);
   for (int i = 0; i < num_equations; i++) temp_values[i] = values[i] + step * (35.0/384.0 * k1[i] + 500.0/1113.0 *
                                                                                k3[i] + 125.0/192.0 * k4[i] -
                                                                                2187.0/6784.0 * k5[i] + 11.0/84.0 * 
                                                                                k6[i]);
   derivative(interval_position + 1 * step, temp_values, k7);

   for (int i = 0; i < num_equations; i ++) value_outputs[i] = values[i] + step * (35.0/384.0 * k1[i] + 500.0/1113.0 *
                                                                                   k3[i] + 125.0/192.0 * k4[i] -
                                                                                   2187.0/6784.0 * k5[i] + 11.0/84.0 *
                                                                                   k6[i]);
   for (int i = 0; i < num_equations; i++) value_errors[i] = step * ((35.0/384.0 - 5179.0/57600.0) * k1[i] +
                                                                                (500.0/1113.0 - 7571.0/16695.0) * k3[i] +
                                                                                (125.0/192.0 - 393.0/640.0) * k4[i] +
                                                                                (92097.0/339200.0 - 2187.0/6784.0) * 
                                                                                 k5[i] + (11.0/84.0 - 187.0/2100.0) *
                                                                                 k6[i] - 1.0/40.0 * k7[i]);                  
}


template <class D>
void AdaptiveRK5<D>::hermite(const double step, D&) {
   
   double value_diff {};
   double b_spline {};
   for (int i = 0; i < num_equations; i++) {
      hermite1[i] = values[i];
      value_diff = value_outputs[i] - values[i];
      hermite2[i] = value_diff;
      b_spline = step * k1[i] - value_diff;
      hermite3[i] = b_spline;
      hermite4[i] = value_diff - step * k7[i] - b_spline;
      hermite5[i] = step * (-12715105075.0/11282082432.0 * k1[i] + 87487479700.0/32700410799.0 * k3[i] +
                            -10690763975.0/1880347072.0 * k4[i] + 701980252875.0/199316789632.0 * k5[i] +
                            -1453857185.0/822651844.0 * k6[i] + 69997945.0/29380423.0 * k7[i]);
   }   
}

template <class D>
std::vector<double> AdaptiveRK5<D>::hermiteOut(const double interval_position, const double step) {
  
   double theta = (interval_position - interval_position_old) / step;
   double theta1 = 1 - theta;
   std::vector<double> hermite_result(num_equations);

   for (int i = 0; i < num_equations; i ++) {
      hermite_result[i] = hermite1[i] + theta * (hermite2[i] + theta1 * (hermite3[i] + theta *
                                         (hermite4[i] + theta1 * hermite5[i]))); 
   } 
   
   return hermite_result; 
}

template <class D>
double AdaptiveRK5<D>::error() {

   double scale {};
   double total_err {};

   for (int i = 0; i < num_equations; i++) {
      scale = absolute_error + relative_error * std::max(std::abs(values[i]), std::abs(value_outputs[i]));
      total_err += ((value_errors[i]/scale) * (value_errors[i]/scale)); 
   }

   return std::sqrt(total_err/num_equations);
}

template <class D>
AdaptiveRK5<D>::Controller::Controller() : reject(false), err_old(1.0e-4) {}

template <class D>
bool AdaptiveRK5<D>::Controller::success(const double err, double& step) {
   
   static const double beta = 0.04;
   static const double alpha = 0.2 - beta * 0.75;
   static const double safe = 0.9;
   static const double min_scale = 0.2;
   static const double max_scale = 10.0; 

   double scale {};
   
   if (err >= 1.0) {
      scale = std::max(safe * std::pow(err, -alpha), min_scale);
      step *= scale;
      reject = true;
      return false;
   }
   else {
      if (err == 0.0) scale = max_scale; 
      else scale = std::max(safe * std::pow(err, -alpha) * std::pow(err_old, beta) , min_scale);
      if (reject) scale = std::min(scale, 1.0);
          
      next_step = step * scale;
      reject = false;
      err_old = std::max(err, 1.0e-4);
      return true;
   }
}

#endif
