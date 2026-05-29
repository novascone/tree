
#ifndef INTERP_H
#define INTERP_H

#include <array>
#include "read.h"

struct TriInterp {

   Read& loaded_data;
   TriInterp(Read& data);
   std::vector<double> interp(std::array<double, 3> position); 
};



#endif
