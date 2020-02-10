def createDeflectionPoints(targetWorkspace:str, InputDataset:str, fcNameDeflectionPoints:str, thresholdValue:float, spatialReferenceObj:object):
    """
    Create a Point feature layer containing the deflection points.
    All units are in meters.
    """

    if arcpy.Exists(fcNameDeflectionPoints):
        ## TEST OUTPUT ##
        logging.debug("Updating existing Deflection points feature layer...")

    tempDataset  = InputDataset + "_TEMP"
    arcpy.management.SplitLine(InputDataset, tempDataset)
    arcpy.management.AddGeometryAttributes(tempDataset,
                   "LINE_BEARING;LINE_START_MID_END", "METERS", "SQUARE_METERS", spatialReferenceObj)
    logging.debug("  Attributes added")
    # Store x, y, and bearing in xyTable
    xyTable = []
    index = 0
    cursor = arcpy.da.SearchCursor(tempDataset, ['START_X', 'START_Y', 'BEARING'])
    for row in cursor:
        xyTable.append((index, row[0],row[1],row[2]))
        index += 1
    del row, cursor
#    arcpy.Delete_management(tempDataset)

    deflection = calculateDeflection(xyTable, thresholdValue)

    defineDeflectionPoints(targetWorkspace, fcNameDeflectionPoints, spatialReferenceObj)
    cursor = arcpy.da.InsertCursor(targetWorkspace + "\\" + fcNameDeflectionPoints,
                        ['POINT_OID','SHAPE@X', 'SHAPE@Y', 'BEARING',
                         'INFLECTION', 'DESCRIPTION','INFLECTION_SIDE'])
    for row in deflection:
        cursor.insertRow(row)
    del cursor
    
    
def calculateDeflection(InputDataset:str, thresholdValue:float):
    """
    Calculate bend angles and determine direction of bend.
    Input table has x (meters), y (meters), bearing (degrees)
    """
    OutputDataset = []
    IndexBearing  = 3

    for i in range(len(InputDataset)-1):

        alpha1 = InputDataset[i  ][IndexBearing]
        alpha2 = InputDataset[i+1][IndexBearing]

        if alpha2 > alpha1 and abs(alpha2 - alpha1) < 180.0:
            phi    = alpha2 - alpha1
            strDir = ['RIGHT','RT']

        elif alpha2 > alpha1 and abs(alpha2 - alpha1) > 180.0:
            phi    = 360.0 - alpha2 + alpha1
            strDir = ['LEFT','LT']

        elif alpha2 < alpha1 and abs(alpha2 - alpha1) < 180.0:
            phi    = alpha1 - alpha2
            strDir = ['LEFT','LT']

        elif alpha2 < alpha1 and abs(alpha2 - alpha1) > 180.0:
            phi    = 360.0 + alpha2 - alpha1
            strDir = ['RIGHT','RT']

        if abs(phi) > thresholdValue:
            dd,mm,ss = decdeg2dms(abs(phi))
            desc     = str(int(dd)) + u'\N{DEGREE SIGN}' + " " + str(int(mm)) + " " + strDir[1]

            OutputDataset.append((InputDataset[i+1][0],
                                  InputDataset[i+1][1],
                                  InputDataset[i+1][2],
                                  InputDataset[i+1][IndexBearing],
                                  phi,desc,strDir[0]))

    return OutputDataset
