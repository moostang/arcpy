def fcXYPointsToLine(Points, wkid, fcLineName):

    """
    Points must have EASTING, NORTHING, and ELEVATION fields.
    """

    xyzList = []
    cursor = arcpy.da.SearchCursor(Points, ['SHAPE@X','SHAPE@Y','ELEVATION'])
    for row in cursor:
        xyzList.append(row)
    del cursor, row


    tblXYtoLine = 'temp_tblXYtoLine'
    arcpy.management.CreateTable(gdb, tblXYtoLine, None, '')
    arcpy.management.AddField(tblXYtoLine, "START_X", "DOUBLE", None, None, None, "START_X", "NULLABLE", "NON_REQUIRED", None)
    arcpy.management.AddField(tblXYtoLine, "START_Y", "DOUBLE", None, None, None, "START_Y", "NULLABLE", "NON_REQUIRED", None)
    arcpy.management.AddField(tblXYtoLine,   "END_X", "DOUBLE", None, None, None,   "END_X", "NULLABLE", "NON_REQUIRED", None)
    arcpy.management.AddField(tblXYtoLine,   "END_Y", "DOUBLE", None, None, None,   "END_Y", "NULLABLE", "NON_REQUIRED", None)
    arcpy.management.AddField(tblXYtoLine, "ELEVATION", "DOUBLE", None, None, None,   "ELEVATION", "NULLABLE", "NON_REQUIRED", None)

    cursor = arcpy.da.InsertCursor(tblXYtoLine,['START_X', 'START_Y', 'END_X', 'END_Y','ELEVATION'])
    for i in range(1,len(xyzList)):
        start_x = xyzList[i-1][0]
        start_y = xyzList[i-1][1]
        end_x   = xyzList[i  ][0]
        end_y   = xyzList[i  ][1]
        z       = (xyzList[i-1][0] + xyzList[i][0])/2.0
        cursor.insertRow((start_x, start_y, end_x, end_y,z))
    del cursor

    arcpy.management.XYToLine(tblXYtoLine, fcLineName, "START_X", "START_Y", "END_X", "END_Y", "GEODESIC", None, wkid)

    arcpy.management.AddField(fcLineName, "ELEVATION", "DOUBLE", None, None, None,   "ELEVATION", "NULLABLE", "NON_REQUIRED", None)

    cursor = arcpy.da.UpdateCursor(fcLineName, ['ELEVATION'])
    i = 1
    for row in cursor:
        row[0] = (xyzList[i-1][2] + xyzList[i][2])/2.0
        i += 1
        cursor.updateRow(row)
    del row, cursor
