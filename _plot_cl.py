# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# FUNCTION _plot_cl
# -----------------
# This function creates a line feature class from an input table.
#
# Workflow:
#
#   1. Create POINT feature class from x-,y-coordinates table using ArcGIS
#      XYTableToPoint function
#   2. Create fields to store x-, y- coordinates for start and end points of
#      LINE centered along the points.
#   3. Create LINE feature class using start and end x-, y- coordinates using
#      ArcGIS XYToLine function.
#
# Input:
#
#   worksheet:
#       PATHNAME of the CSV file containing the survey data for the centerline.
#       These units of this data is usually in meters if it's spatial reference
#       is Universal Transverse Mercator (UTM). The key fields are:
#       CHAINAGE,   The chainage values in meters (FLOAT)
#       EASTING,    The UTM's Easting value in meters (FLOAT)
#       NORTHING,   The UTM's Northing value in meters (FLOAT)
#       ELEVATION,  The recorded Elevation in meters (FLOAT)
#       CID,        Unique Centerline ID/Name. (INTEGER)
#
#   sr:
#       ArcGIS OBJECT containgng Spatial Reference information.
#
#   xField, yField, mField:
#       These are NAMES of fields in the input worksheet to be used for x, y,
#       and chainage values.
#
#   OUTPUT:
#
#   xyPointFile:
#       NAME of POINT feature class to be created from centerline table.
#
#   xyLine:
#       NAME of LINE feature class to be created from xyPointFile
#
# Usage:
#       _plot_cl("Centerline_Sheet1.csv", sr, 'EASTING', 'NORTHING', 'CHAINAGE', "points_file", "centerline")

# FileName: _plot_cl.py
# Created on: 2019-03-20 (Moostang)
# --------------------------------------------------------------------------- #
def _plot_cl(worksheet, sr, xField, yField, mField, xyPointFile, xyLine):

    # Create x-y Point Feature
    # ------------------------
    # Create output xyPointFile POINT feature class from input worksheet CSV
    # file. Use 'EASTING' and 'NORTHING' for x- and y-coordinates, and sr as
    # the spatial reference.
    arcpy.management.XYTableToPoint(worksheet, xyPointFile, xField, yField, None, sr)
    arcpy.AddMessage('Converting {0} to Point Feature Class {1}'.format(worksheet, xyPointFile))

    # Prepare x-y Point feature
    # -------------------------
    # Add fields in the attribute table of xyPointFile to define the starting
    # and ending coordinates of the LINE feature to create. These fields are
    # start_x, start_y, end_x, and end_y and are tabulated by translating the
    # northing and easting values for respective points.
    arcpy.AddField_management(xyPointFile, "START_X", "DOUBLE", 15, "", "", "START_X", "NULLABLE")
    arcpy.AddField_management(xyPointFile, "START_Y", "DOUBLE", 15, "", "", "START_Y", "NULLABLE")
    arcpy.AddField_management(xyPointFile,   "END_X", "DOUBLE", 15, "", "",   "END_X", "NULLABLE")
    arcpy.AddField_management(xyPointFile,   "END_Y", "DOUBLE", 15, "", "",   "END_Y", "NULLABLE")
    arcpy.AddMessage('Fields for start and end x-y values are added to {0}'.format(xyPointFile))

    # Check for NULL values
    # ---------------------
    # Check if there are null values after the last point in the worksheet.
    # Rows with NULL values of NORTHING and EASTING needs to be deleted prior
    # to constructing GEODESIC line from the x-y points Table.
    arcpy.AddMessage('Checking for NULL values')
    with arcpy.da.SearchCursor(xyPointFile, yField) as cursor:
        icount = 0
        for row in cursor:
            if not (row[0] is None):
                icount = icount + 1

    l = icount # Total number of rows

    xValues = []
    yValues = []

    # Assign Starting Coordinates
    # ---------------------------
    # Assign x-y coordinate values at given point as the x-y coordinate for the
    # start point of the LINE feature class
    with arcpy.da.UpdateCursor(xyPointFile, [yField, xField, 'START_X', 'START_Y']) as cursor:
        for row in cursor:
            row[2] = row[1]
            row[3] = row[0]
            xValues.append(row[1])
            yValues.append(row[0])

            cursor.updateRow(row) # Update the cursor with the updated list

    arcpy.AddMessage('Starting Coordinates Assigned')
    del cursor, row


    # Assign Ending Coordinates
    # -------------------------
    # Assign x-y coordinate values at the next point as the x-y coordinate for
    # the end point of the LINE feature class
    with arcpy.da.UpdateCursor(xyPointFile, [yField, xField, 'END_X', 'END_Y']) as cursor:
        icount = 1
        for row in cursor:
            if icount < l:
                row[2] = xValues[icount]
                row[3] = yValues[icount]

            if icount == l:
                row[2] = xValues[l-1]
                row[3] = yValues[l-1]

            icount = icount + 1

            cursor.updateRow(row) # Update the cursor with the updated list

    arcpy.AddMessage('Ending Coordinates Assigned')
    del cursor, row

    # Delete rows with NULL values.
    # -----------------------------
    with arcpy.da.UpdateCursor(xyPointFile, yField) as cursor:
        icount = 0
        for row in cursor:
            if (row[0] is None):
                cursor.deleteRow()
    arcpy.AddMessage('NULL values Deleted')
    del cursor, row

    # Create LINE feature class
    # -------------------------
    # Draw GEODESIC lines from the start and end X-Y coordinate values
    arcpy.AddMessage('Creating LINE feature class {0} from {1}.'.format(xyLine, xyPointFile))
    arcpy.management.XYToLine(xyPointFile, xyLine, "START_X", "START_Y", "END_X", "END_Y", "GEODESIC", mField, sr)
    arcpy.AddMessage('LINE feature class {0} created.'.format(xyLine))

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #