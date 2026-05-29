
#ifndef OUTPUT_H
#define OUTPUT_H

#include <vector>

struct Output {
   
   int capacity {}; 
   int num_equations {}; 
   int num_saved {}; 
   bool hermite_out;
   int count {}; 
   double interval_start {}; 
   double interval_end {}; 
   double interval_out {}; 
   double interval_diff_out {}; 
   std::vector<double> interval_saved; 
   std::vector<std::vector<double>> values_saved; 

   Output(): capacity(-1), hermite_out(false), count(0) {}  
   Output(const int num_saved_p): capacity(500), num_saved(num_saved_p), count(0), interval_saved(capacity) {

      hermite_out = num_saved > 0 ? true : false;
   }

   void init(const int num_equations_p, const double interval_low, const double interval_hi){ 

      num_equations = num_equations_p;
      
      if (capacity == -1) return;
      values_saved.resize(capacity);
      
      if (hermite_out) {
   
         interval_start = interval_low;
         interval_end = interval_hi;
         interval_out = interval_start;
         interval_diff_out = (interval_end - interval_start)/ num_saved;
      }  
   }

   void resize() { 

      capacity*=2;      
      interval_saved.resize(capacity); 
      values_saved.resize(capacity);
   } 
      
   
   template <class Stepper>
   void saveHermite (Stepper& stepper, const double interval_out, const double step) {
      
      if (count == capacity) resize(); 
      values_saved[count] = stepper.hermiteOut(interval_out, step); 
      interval_saved[count++] = interval_out;
   }

   void save(const double interval_pos, std::vector<double>& values) {

      if (capacity <= 0) return;
      if (count == capacity) resize();
      values_saved[count] = values; 
      interval_saved[count++] = interval_pos;
   }

   template <class Stepper>
   void out (const int num_steps, const double interval_pos, std::vector<double>& values, Stepper& stepper,
             const double step) {

      if (!hermite_out) throw("Hermite output not set");

      if (num_steps == -1) {
         save(interval_pos, values);
         interval_out += interval_diff_out;
      }
      else {
   
         while ((interval_pos - interval_out) * (interval_end - interval_start) > 0.0) {
         
            saveHermite(stepper, interval_out, step);
            interval_out += interval_diff_out;
         }
      }
   } 
};

#endif
