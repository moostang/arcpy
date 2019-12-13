# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# Created on: March 20, 2019
# Updated on: April 26, 2019
# Updated on: December 13, 2019
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# Project Geographic System for Input Data
# --------------------------------------------------------------------------- #
# String below is representation for the
# Geographic Coordinate system "WGS 1984" (factory code=4326)

import arcpy

def Create_START_END_From_XY_Points(InputDataset:str):
    """
    Create a line with segments in between the x-y points. This script will
    generate four columns containing START_X, START_Y, END_X, END_Y in the
    attribute table of a Points feature class.
    """

    import arcpy

    # Create start_x, start_y, end_x, and end_y for each point
    arcpy.management.AddField(InputDataset, 'START_X', "DOUBLE", 15, None, None, 'START_X', "NULLABLE", "NON_REQUIRED", None)
    arcpy.management.AddField(InputDataset, 'START_Y', "DOUBLE", 15, None, None, 'START_Y', "NULLABLE", "NON_REQUIRED", None)

    arcpy.management.AddField(InputDataset, 'END_X', "DOUBLE", 15, None, None, 'END_X', "NULLABLE", "NON_REQUIRED", None)
    arcpy.management.AddField(InputDataset, 'END_Y', "DOUBLE", 15, None, None, 'END_Y', "NULLABLE", "NON_REQUIRED", None)

    xValues = []
    yValues = []
    with arcpy.da.UpdateCursor(InputDataset, ['SHAPE@X', 'SHAPE@Y', 'START_X', 'START_Y']) as cursor:
        for row in cursor:
            row[3] = row[0]
            row[4] = row[1]
            row[5] = row[2]
            xValues.append(row[0])
            yValues.append(row[1])
    del cursor, row

    totalRows = int(arcpy.GetCount_management(InputDataset)[0])

    with arcpy.da.UpdateCursor(InputDataset, ['END_X', 'END_Y']) as cursor:
        icount = 1
        for row in cursor:
            if icount < totalRows:
                row[0] = xValues[icount]
                row[1] = yValues[icount]
            if icount == totalRows:
                row[0] = xValues[totalRows-1]
                row[1] = yValues[totalRows-1]
            icount = icount + 1

            # Update the cursor with the updated list
            cursor.updateRow(row)
    del cursor, row

    # If Z coordinates are available
    if arcpy.Describe(InputDataset).hasZ:
        arcpy.management.AddField(InputDataset, 'START_Z', "DOUBLE", 15, None, None, 'START_Z', "NULLABLE", "NON_REQUIRED", None)
        arcpy.management.AddField(InputDataset, 'END_Z', "DOUBLE", 15, None, None, 'END_Z', "NULLABLE", "NON_REQUIRED", None)

        ZValues = []
        with arcpy.da.UpdateCursor(InputDataset, ['SHAPE@Z', 'START_Z']) as cursor:
            for row in cursor:
                row[1] = row[0]
                zValues.append(row[0])
        del cursor, row

        with arcpy.da.UpdateCursor(InputDataset, ['END_Z']) as cursor:
            icount = 1
            for row in cursor:
                if icount < totalRows:
                    row[0] = zValues[icount]
                if icount == totalRows:
                    row[0] = zValues[totalRows-1]
                icount = icount + 1

                # Update the cursor with the updated list
                cursor.updateRow(row)
        del cursor, row


    # Delete last row
    rows = [row for row in arcpy.da.SearchCursor(InputDataset, 'OBJECTID')] # Search with OBJECTID. If searching with other fields, SORT THEM FIRST !!!
    lastRowObjectID = rows[-1][0]
    arcpy.management.SelectLayerByAttribute(InputDataset, "NEW_SELECTION", "OBJECTID = " + str(lastRowObjectID), None)
    arcpy.management.DeleteRows(InputDataset)

def getUserInput():
    """
    Fetches argument variables from python program. Returns a list of argument
    variables.
    """
    # USER INPUT
    # ------------------------------------------------------------------------ #
    argumentList = sys.argv
    print(argumentList)

    csvFile_or_Sheet = sys.argv[1]
    fc_XYToPoints = sys.argv[2]
    strField_X = sys.argv[3]
    strField_Y = sys.argv[4]
    strField_Z = sys.argv[5]
    xyLine = sys.argv[6]
    wkid = sys.argv[7]

    SpatialReferenceObj = arcpy.SpatialReference(wkid)

    return csvFile_or_Sheet, fc_XYToPoints, strField_X, strField_Y, strField_Z, xyLine, SpatialReferenceObj

def main():

    csvFile_or_Sheet, fc_XYToPoints, strField_X, strField_Y, strField_Z, xyLine, srObj = getUserInput()

    if strField_Z:
        arcpy.management.XYTableToPoint(csvFile_or_Sheet, fc_XYToPoints, strField_X, strField_Y, strField_Z, srObj)
    else:
        arcpy.management.XYTableToPoint(csvFile_or_Sheet, fc_XYToPoints, strField_X, strField_Y, None, srObj)

    Create_START_END_From_XY_Points(fc_XYToPoints)

    # Draw line from X-Y points
    arcpy.management.XYToLine(fc_XYToPoints, xyLine, "START_X", "START_Y", "END_X", "END_Y", "GEODESIC", "CHAINAGE", srObj)

if __name__ == '__main__':
    main()
