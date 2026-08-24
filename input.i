[Geometry]
   [main_sphere]
     type = sphere 
     radius = 6371000.0
     resolution = 64
   []
[]

[Fields]
  [HWM]
     type = vector 
     source = ~/HWM_Data/hwm_wind_field.nc
     grid_type = structured
     variables = u_mer u_zon
     variable_directions = +lat +lon
     variable_units = m/s m/s
     coordinates = lat lon alt
     coordinate_units = degree degree km 
     coordinate_system = geographic
     periodic = lon
     vector_convention = ENU
  []
  [NAVGEM]
   type = vector
   source = ~/navgem-data/navgem_reanalysis_X0360Y0180ZL111_slfull_uniform_2024052600_000004.h5
   grid_type = structured
   variables = /Meteorology/zonal_wind /Meteorology/meridional_wind
   variable_directions = +lon +lat 
   variable_units = m/s m/s
   coordinates = /Geometry/Geometric_height_levels /Geometry/Latitudes_1d /Geometry/Longitudes_1d 
   coordinate_units = m degree degree
   coord_order = alt lat lon
   coordinate_system = geographic
   periodic = lon
   vector_convention = ENU
   sentinel = -99999.0
  [] 
[]
