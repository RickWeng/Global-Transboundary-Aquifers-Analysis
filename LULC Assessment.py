### Script name: Assessment of land use and land cover change above global transboundary aquifers
### Description: This script is created to understand (1) transformation of land use type above each aquifer over the past century (2) forest cover loss above transboundary aquifers from 2000 to 2014.
## Goal of the script:
    # Goal 1: Derive table of dominant land use type for each aquifer in 1900 and 2000 (Data used for Figure 2 in project summary)
    # Goal 2: Derive forest class raster from tree cover raster
    # Goal 3: Derive forest loss data within tree cover >= 50% (i.e. forests)
    # Goal 4: Derive data for calculating gross forest loss rate from 2000 to 2014 (Data used for Figure 3 in project summary)
# Author: Ricky Weng
# Revised by: Ricky Weng
# Written: Dec 2nd, 2017
# Revised: Dec 3rd, 2017
# ------------------------------------------------------------------------------------------------------



# Goal 1: Derive table of dominant land use type for each aquifer in 1900 and 2000
########################################################################################################

# Import arcpy module
import arcpy
from arcpy import env
from arcpy.sa import *

# Check out spatial tool license
arcpy.CheckOutExtension("spatial")

# Set geoprocessing environments
arcpy.env.workspace = "C:\\Ricky\\Anthrome.gdb"
arcpy.env.scratchWorkspace = "C:\\Ricky\\scratch.gdb"    

# Define input variables:
TBA = "TBA2015" # Transboundary aquifers shapefile
a1900 = "anthro2_a1900" # Anthropogenic biomes in year 1900
a2000 = "anthro2_a2000" # Anthropogenic biomes in year 2000

# Define output variables:
TBA_Raster = "TBA2015_Raster" # Transboundary aquifers raster
Reclass_1900 = "Reclass_a1900" # Reclassified anthropogenic biomes in year 1990
ZS_1900 = "ZonalSt_a1900" # Table of statistics of anthropogenic biomes in each aquifer in 1990
Reclass_2000 = "Reclass_a2000" # Reclassified anthropogenic biomes in year 2000
ZS_2000 = "ZonalSt_a2000" # Table of statistics of anthropogenic biomes in each aquifer in 2000

# Step 1: Change transboundary aquifer polygons to raster
# Process: Polygon to Raster
if arcpy.Exists(TBA_Raster): arcpy.Delete_management(TBA_Raster)
arcpy.PolygonToRaster_conversion(TBA, "OBJECTID", TBA_Raster, "CELL_CENTER", "NONE", a1900)

# Step 2: Reclassify anthrome in 1900 and 2000 to 6 broad categories (dense, villages, croplands, rangelands, seminatural, wildlands)
# Process: Reclassify
if arcpy.Exists(Reclass_1900): arcpy.Delete_management(Reclass_1900)
arcpy.gp.Reclassify_sa(a1900, "VALUE", "11 1;12 1;21 2;22 2;23 2;24 2;31 3;32 3;33 3;34 3;41 4;42 4;43 4;51 5;52 5;53 5;54 5;61 6;62 6", Reclass_1900, "DATA")
if arcpy.Exists(Reclass_2000): arcpy.Delete_management(Reclass_2000)
arcpy.gp.Reclassify_sa(a2000, "VALUE", "11 1;12 1;21 2;22 2;23 2;24 2;31 3;32 3;33 3;34 3;41 4;42 4;43 4;51 5;52 5;53 5;54 5;61 6;62 6", Reclass_2000, "DATA")

# Step 3: Derive tables of statistics of anthromes for each aquifer in 1900 and 2000
# Process: Zonal Statistics as Table
if arcpy.Exists(ZS_1900): arcpy.Delete_management(ZS_1900)
arcpy.gp.ZonalStatisticsAsTable_sa(TBA_Raster, "Value", Reclass_1900, ZS_1900, "DATA", "ALL")
if arcpy.Exists(ZS_2000): arcpy.Delete_management(ZS_2000)
arcpy.gp.ZonalStatisticsAsTable_sa(TBA_Raster, "Value", Reclass_2000, ZS_2000, "DATA", "ALL")



# Goal 2: Make tree cover raster (0-100%) to forest class raster (0,1) where 0 means tree cover <50%, 1 means tree cover >=50%
##############################################################################################################################

# Import modules
import os
import glob
from arcpy import *
from arcpy import env
from arcpy.sa import *

# Call spatial extension
arcpy.CheckOutExtension("Spatial")

# Set the geoprocessing environments
arcpy.env.workspace = "C:\\Ricky\\rename cover raster"

# Define input variables
treecover = "C:\\Ricky\\rename cover raster\\" # Renamed tree cover raster files. Tree cover in year 2000. Encoded as a percentage per output grid cell, in the range 0-100.
addtree = ".tif"
treecoverlist = []

# Output variables
OutDir ="C:\\Ricky\\tree cover 50\\"
Outlist = []

# Step 1: Change original tree cover file name to a series of numbers (original global tree cover datasets were stored in hundreds of tiles) 
os.chdir ("C:\\Ricky\\rename cover raster")
print os.getcwd()
i = 0
for file in os.listdir("C:\\Ricky\\Directed Study\\rename cover raster"):
    i += 1
    new_file_name = "{}.tif". format(i)
    os.rename(file,new_file_name)

# Step 2: Convert tree cover to forest class where 0 means non-forest (tree cover <50%), 1 means forest (tree cover >= 50%)
# use loop to read, process and output the data
for i in range (1,181):
    treecoverlist = treecover + str(i)+ addtree
    # Process: Con (>=50 then 1; otherwise 0)
    outCon = Con(treecoverlist, 1, 0, "Value>=50")
    Outlist = OutDir + str(i)
    if arcpy.Exists(Outlist): arcpy.Delete_management(Outlist)
    outCon.save(Outlist)
    print (outCon)



# Goal 3: Derive forest loss data within tree cover >= 50% (i.e. forests)
########################################################################################################

# Import arcpy module
import os
import glob
from arcpy import *
from arcpy import env
from arcpy.sa import *

# Call spatial extension
arcpy.CheckOutExtension("Spatial")

# Set the geoprocessing environments
arcpy.env.workspace = "C:\\Ricky\\rename forest loss"

# Define input variables
forestcover = "C:\\Ricky\\tree cover 50\\" # Forest cover raster derived from previous goal 2. 0 means non-forests, 1 means forests.
addcover = ".tif"
forestcoverlist = []
forestloss = "C:\\Ricky\\rename forest loss\\" # Renamed forest loss year raster. Forest loss during 2000-2014. Encoded as either 0 (no loss) or else a value in the range 1-14, representing loss detected primarily in the year 2001-2014, respectively.
addforest = ".tif"
forestlist = []

# Output variables
OutDir = "C:\\Ricky\\forest loss within forests\\"
Outlist = []

# Step 1: Change original forest loss year file name to a series of numbers which correspond to tree cover file name(original global forest loss year datasets were stored in hundreds of tiles) 
os.chdir ("C:\\Ricky\\rename forest loss")
print os.getcwd()
i = 0
for file in os.listdir("C:\\Rikcy\\rename forest loss"):
    i += 1
    new_file_name = "{}.tif". format(i)
    os.rename(file,new_file_name)

# Step 2: Derive forest loss year raster data within forest class (i.e. tree cover >= 50%)
for i in range (1,181):
    forestcoverlist = forestcover + str(i) + addcover
    forestlosslist = forestloss + str(i) + addforest
    print forestcoverlist
    print forestlosslist
    # Process: Con (when loss occurs in forests, give forest cover the original value of forest loss year (0-14, indicate year of loss); when loss occurs in non-forests, assign 15)
    outCon = Con(forestcoverlist,forestlosslist, 15, "Value=1")
    Outlist = OutDir + str(i)
    if arcpy.Exists(Outlist): arcpy.Delete_management(Outlist)
    outCon.save(Outlist)
    print (outCon)



# Goal 4: Derive data for calculating gross forest loss rate for each aquifer from 2000 to 2014
########################################################################################################

# Import arcpy module
from arcpy import *
from arcpy import env
from arcpy.sa import *

# Call spatial extension
arcpy.CheckOutExtension("Spatial")

# Set the geoprocessing environments
arcpy.env.workspace = "C:\\Ricky\\forest loss within forests"
# Import the spatial analyst supplemental tools which include improved tabulate area tool
arcpy.ImportToolbox("C:\\Ricky\\Downloads\\SpatialAnalystSupplementalTools\\SpatialAnalystSupplementalTools\\Spatial Analyst Supplemental Tools.pyt")

# Define input variables
forestloss = arcpy.ListRasters()# forest loss raster when forest loss occurs within tree cover >= 50% (derived from previous goal 3)
print (forestloss)
aquifers = "C:\\Ricky\\TBA2015.shp" # Transboundary aquifers shapefile

# Output variables
outFolder = "C:\\Ricky\\table of forest loss"
outTable = []
aquifers_Raster = "C:\\Ricky\\TBA2015_Raster" # Transboundary aquifers raster

# Step 1: Change transboundary aquifer polygons to raster (resolution same as forest loss raster)
# Process: Polygon to Raster
if arcpy.Exists(aquifers_Raster): arcpy.Delete_management(aquifers_Raster)
arcpy.PolygonToRaster_conversion(aquifers, "OBJECTID", aquifers_Raster, "CELL_CENTER", "NONE",27.668035415188)

# Step 2: Derive table of data for calculating gross forest loss rate for each aquifer from 2000 to 2014
# use loop to read, process and output the data
for inRaster in forestloss:
    outTable = outFolder + "table" + inRaster
    # check the outputs
    if arcpy.Exists(outTable): arcpy.Delete_management(outTable)
    # processing: Tabulate Area
    arcpy.TabulateArea02_sas(aquifers_Raster, "OBJECTID", inRaster, "VALUE", outTable, 27.668035415188)
    print(outTable)

