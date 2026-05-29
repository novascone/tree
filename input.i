[Geometry]
   [main_sphere]
     type = sphere 
     radius = 6371.0
     resolution = 64
   []
[]

[Fields]
  [EM]
     TYPE = VECTOR
     source = ~/HWM_Data/hwm_wind_field.nc
     grid_type = structured
     variables = u_mer u_zon 
     coordinates = lat lon alt 
     [render]
      line_type = straight
      colormap = some_colormap
      seed_count = 100 
      seed_distribution = uniform
     []
  []
  [Temperature]
   type = scalar
   source = some_data
   grid_type = structured
   [render]
    colormap = some_colormap
   []
  [] 
[]
