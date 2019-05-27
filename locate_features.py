# Locate features (polygons, lines, points) along a route
# -------------------------------------------------------
# Created on: 2019/05/27
#
# Import packages
import arcpy

# Input Parameters
# ----------------
# gdb, Path of geodatabase
# fcRoute,  Feature class from which route is created
# RID,      Route identification number of feature class associated with the
#       intersecting feature classes.
# route,    Route feature class
# description, This field must be present in all of the feature classes that intersect (crosses)
#       with the   <fcRoute>  .
#



gdb = 'C:/GIS/ROUTE_PROJECT.gdb'
RID = 'RID'
radius = '10 Meters'
route = 'MY_ROUTE'
myDataset = "MAP_ELEMENTS"
# Set Workspace where map elements are stored
arcpy.env.workspace = gdb

routeTbl = []

# Locate POLYGON Features Along Routes
items = arcpy.ListFeatureClasses("*","POLYGON",myDataset)
for fc in items:

    # Fetch starting and ending chainage values for intersecting polygon
    # feature
    outTable = "RT_" + fc
    arcpy.lr.LocateFeaturesAlongRoutes(fc, route, RID, radius , outTable, RID + " Line FMEAS TMEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
    #arcpy.AddMessage("Feature {0} located for route {1}".format(fc, route))
    print(outTable)

    # Arrange feature
    with arcpy.da.SearchCursor(outTable, [RID,'TMEAS','Description']) as cursor:
        j = 0
        for row in cursor:
            j = j + 1

    print("j = " + str(j))
    print(" ")
    if j > 0:
        del row, cursor
        with arcpy.da.SearchCursor(outTable, [RID,'TMEAS','Description']) as cursor:
            i = 0
            fmeas = []
            desc = []
            ridList = []
            for row in cursor:
                if not row[2]:
                    row[2] = "empty"
                ridList.append(row[0])
                fmeas.append(row[1])
                desc.append(row[2])
                i = i + 1
            #arcpy.AddMessage("There are {0} rows in {1}".format(i, outTable))
            print(i)

        del row, cursor

        with arcpy.da.UpdateCursor(outTable, ['Description']) as cursor:
            for row in cursor:
                print(row[0])
                row[0] = "Begin " + row[0]
                print(row[0])
                cursor.updateRow(row)
                print("Updating description")

        del row, cursor

        cursor = arcpy.da.InsertCursor(outTable,['RID', 'FMEAS', 'Description'])
        for x in range(i):
            cursor.insertRow((ridList[x], fmeas[x], "END of " + desc[x]))
            print("inserting row")
        del cursor

        arcpy.DeleteField_management(outTable, ['TMEAS'])

        routeTbl.append(outTable)

    else:
        arcpy.Delete_management(outTable)

    print(" ")
    print(" ")


# Locate LINE Features Along Routes
items = arcpy.ListFeatureClasses("*","LINE",myDataset)
for fc in items:

    fcTemp = "TEMP_route_intersect"
    arcpy.analysis.Intersect(route + " #;'"+ fc +"' #", fcTemp, "ALL", "0.001 Meters", "POINT")

    # Fetch starting and ending chainage values for intersecting polygon
    # feature
    outTable = "RT_" + fc
    arcpy.lr.LocateFeaturesAlongRoutes(fcTemp, route, RID, radius , outTable, RID + " Point FMEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
    arcpy.AddMessage("Feature {0} located for route {1}".format(fc, route))

    cursor = arcpy.da.SearchCursor(outTable, [RID,'FMEAS','Description'])

    arcpy.Delete_management(fcTemp)

    if len(cursor.fields) == 0:
        arcpy.Delete_management(outTable)
    else:
        routeTbl.append(outTable)


# Locate POINT Features Along Routes
items = arcpy.ListFeatureClasses("*","POINT",myDataset)
for fc in items:

    # Fetch starting and ending chainage values for intersecting polygon
    # feature
    outTable = "RT_" + fc
    arcpy.lr.LocateFeaturesAlongRoutes(fc, route, RID, radius , outTable, RID + " Point FMEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
    arcpy.AddMessage("Feature {0} located for route {1}".format(fc, route))

    cursor = arcpy.da.SearchCursor(outTable, [RID,'FMEAS','Description'])

    arcpy.Delete_management(fcTemp)

    if len(cursor.fields) == 0:
        arcpy.Delete_management(outTable)
    else:
        routeTbl.append(outTable)








