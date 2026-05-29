

# Journal

## Decisions

### Pybind to Hand Data from Python to C++
Chose to use pybind to hand data to and from C++. This decision was made for two main reasons.
First, loading large data files searching them and interpolating is slow in Python. Second 
Blenders API is in Python, so it's easiest to have all the data we want to hand to blender in Python.
Why C++? Lots of scientific computation library support over a language like Rust. Blender is written
in C++ so connecting the two would be easier if need be. 

### Conda for Managing Dependencies
Conda makes it easy to gather all dependencies in one isolated environment. This allows us to 
depend on NetCDF libraries, Exodus libraries, VTK libraries etc. Simple to install, and makes TREE 
only require, conda, a C++ compiler, and Blender. Simple.

### Three C++ Layers
Three distinct layers that handle, reading data and storing it in memory, interpolating between points, 
and integrating for the path. This is important for keeping TREE format agnostic. No layer should need to know
about another. If TREE supports opening a file type that data can be visualized. 

### Deriv Overloading for Coordinate Systems
The `Deriv` functor passed to the integrator assumes the state vector and field values share units. For geographic
coordinate systems (lat/lon/alt) with winds in m/s, a separate `GeographicDeriv` overload handles the unit
conversion (m/s → degrees/s) via the standard 111 km/degree scaling for lat and cos(lat) correction for lon.
`driveField` selects the correct functor based on `FieldConfig::coordinate_system`. This keeps unit assumptions
out of the core integrator and avoids hardcoded branching inside a single struct.

## References

## Acknowledgements
**Numerical Recipes (3rd ed.)** C++ architecture

## Methods
**Claude (Anthropic)** - AI model used to help find resources, debug and refine code


