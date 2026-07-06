[Geometry]
   [main_sphere]
     type = sphere 
     radius = 6371.0
     resolution = 64
   []
[]

[Fields]
  [HWM]
     type = vector 
     source = ~/HWM_Data/hwm_wind_field.nc
     grid_type = structured
     variables = u_mer u_zon 
     coordinates = lat lon alt
     coordinate_system = geographic 
  []
  [NAVGEM]
   type = vector
   source = ~/navgem-data/navgem_reanalysis_X0360Y0180ZL111_slfull_uniform_2024052600_000004.h5
   grid_type = structured
   variables = /Meteorology/zonal_wind /Meteorology/meridional_wind
   coordinates = /Geometry/Geometric_height_levels /Geometry/Latitudes_1d /Geometry/Longitudes_1d 
   coord_order = alt lat lon
   coordinate_system = geographic
  []
  [AWE]
   type = scalar
   source = ~/awe-data/awe_l3c_q20_2024146T2343_02882_v01.nc
   grid_type = unstructured
   variables = Radiance
   coordinates = Latitude Longitude 
   coordinate_system = geographic
   altitude = 85
  [] 
[]
