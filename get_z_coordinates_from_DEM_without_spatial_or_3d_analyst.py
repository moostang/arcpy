#-------------------------------------------------------------------------------
# Name:        get_z_coordinates_from_DEM_without_spatial_or_3d_analyst
# Purpose:     Generate z-coordinate values from input DEM without Spatial or
#              3D Analyst
#
# Author:      moostang
#
# Created:     20-11-2019, 10:00 AM
#-------------------------------------------------------------------------------
import arcpy

def GetCellValue(demPath:str, fcPath:str) -> list:

    cursor = arcpy.da.SearchCursor(fcPath,['POINT_X', 'POINT_Y'])
    xyList = []
    for row in cursor:
        xyList.append((row[0], row[1]))
    del row, cursor

    xyzList = []
    index = 0
    for row in xyList:

        ## TEST OUTPUT ##
        print("Getting cell value for row {0}".format(index))


        xyPair = str(row[0]) + " " + str(row[1])
        result = arcpy.GetCellValue_management(demPath, xyPair, "1")
        xyzList.append((row[0], row[1], float(result.getOutput(0))))
        index += 1

    return xyzList

def AddElevationField(fcName:str, xyzList:list):

    arcpy.management.AddField(fcName, "POINT_Z", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')

    cursor = arcpy.da.UpdateCursor(fcName, ['POINT_X', 'POINT_Y', 'POINT_Z'])
    index = 0
    for row in cursor:
        if row[0] == xyzList[index][0] and row[1] == xyzList[index][1]:
            row[2] = xyzList[index][2]
            cursor.updateRow(row);
        index += 1
    del row, cursor

def main():

    rootfolder = "C:\\GIS\\Open_Data"
    gdb = rootfolder + "\\Open_Data.gdb"
    demPath = rootfolder + "\\DEM.tif"
    temp = rootfolder + "\\CENTERLINE.shp"
    fcPath = gdb + "\\CENTERLINE_POINTS"
    xlsPath = rootfolder + "\\XYZ.xlsx"


    distance = 5
    wkid = 2955  # NAD83 (CSRS) UTM 11N ZONE

    arcpy.management.GeneratePointsAlongLines(temp, fcPath, "DISTANCE", str(distance) + " Meters", None, "END_POINTS")
    arcpy.management.AddGeometryAttributes(fcPath, "POINT_X_Y_Z_M", "METERS", "SQUARE_METERS", wkid)

    xyzList = GetCellValue(demPath, fcPath)
    AddElevationField(fcPath, xyzList)

    arcpy.conversion.TableToExcel(fcPath, xlsPath, "NAME", "CODE")

if __name__ == '__main__':
    main()
