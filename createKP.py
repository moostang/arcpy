# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
def createKP(gdb, fcCenterline, fcKP, sr):

    # Function to create kilometer post and points at every 100 m along the
    # centerline
    #
    # NOTES
    #
    # What do we do about bends? are we sure that there are not bends ?
    #
    # Input
    # gdb      Geodatabase
    # fcCenterline, Input Feature class from which the chainage values are
    #          read. This table must also contain 'NORTHING' and 'EASTING'
    #          values.
    # sr       Spatial reference object
    #
    # USAGE
    # createKP('C:/GIS/Pipeline/pipeline.gdb','featurefile.shp','KP.shp',sr)
    # ------------------------------------------------------------------------ #
    import numpy as np
    import math


    arcpy.env.workspace = gdb

    # Set local variables
    has_m = "DISABLED"
    has_z = "DISABLED"
    #
    incrementKP = 100                      # increment value for KP

    # Make new feature (point)
    arcpy.CreateFeatureclass_management(gdb, fcKP, "POINT","", has_m, has_z, sr)

    # Make new column
    arcpy.AddField_management(fcKP, "KP", "LONG", 9,"", "", "KP", "NULLABLE")
    arcpy.AddField_management(fcKP, "EASTING", "DOUBLE", 15, "", "", "EASTING", "NULLABLE")
    arcpy.AddField_management(fcKP, "NORTHING", "DOUBLE", 15, "", "", "NORTHING", "NULLABLE")
    arcpy.AddField_management(fcKP, "ANGLE", "DOUBLE", 15, "", "", "ANGLE", "NULLABLE")

    # Put required data in a list
    dataList = []
    cursor = arcpy.da.SearchCursor(fcCenterline, ['CHAINAGE','NORTHING', 'EASTING'])
    if isinstance(cursor.fields[0],str):
        # Check if field is a non-numeric field
        for row in cursor:
            # If the CHAINAGE field is a STRING
            try:
                dataList.append((float(row[0]),row[1],row[2]))
            except:
                # print("Error at row" + str(dataLength+1) )
                break
        else:
            # If CHAINAGE field is NOT a string
            dataList.append((row[0],row[1],row[2]))

    del cursor, row

    # Now sort data to contain rows with increasing chainage values
    tempList =[]
    tempList.append(dataList[0])
    for i in range(1,len(dataList)):
        # Check to see if CHAINAGE values are increasing from one row to another.
        pt1Chainage = dataList[i-1][0]
        pt2Chainage = dataList[i  ][0]
        if pt2Chainage >= pt1Chainage:
            tempList.append(dataList[i])
        else:
            #print("Smaller values at row " + str(i))
            continue


    del pt1Chainage, pt2Chainage

    # Create list to store KP values
    # temp = math.ceil((data[l-1,3]/100))*100 # Find maximum chainage value
    # KPdata = np.zeros((temp/incrementKP,3))
    # del temp
    KPlist = []

    # Calculate x-y coordinate values for KP points by applying simple
    # Pythagorous theorem
    #
    #
    #                p_pt2-pt1   y_pt2 - y_pt1
    #   tan(theta) = --------- = -------------
    #                b_pt2-pt1   x_pt2 - x_pt1
    #
    #                y_pt2 - y_pt1
    #   theta = atan -------------
    #                x_pt2 - x_pt1
    #
    #   h_new = KP_value - chainage_pt1
    #
    #   p_new = h_new sin(theta)
    #   b_new = h_new cos(theta)
    #
    #   x_new = x_pt1 + b_new
    #   y_new = y_pt1 + p_new
    #
    valueKP = math.floor((tempList[0][0]/100))*100 # Floor the first chainage value
    valueKP = valueKP + incrementKP
    for i in range(1,len(tempList)-1):
        if(tempList[i][0] >= valueKP):

            y1 = tempList[i-1][1]
            x1 = tempList[i-1][2]
            y2 = tempList[i  ][1]
            x2 = tempList[i  ][2]

            numer = y2-y1
            denom = x2-x1
            h = valueKP - tempList[i-1][0]

            # Check if denominator is zero
            if denom == 0:
                # pt2 is directly above or below pt1
                p = h
                b = 0
            else:
                # Denominator is NOT zero
                theta = math.atan( numer/denom  )
                p = h*math.sin(theta)
                b = h*math.cos(theta)

            x = x1 + b
            y = y1 + p

            KPlist.append((valueKP,(x,y)))

            valueKP = valueKP + incrementKP # Calculate KP value for next KP point
            # m = m + 1 # Increase counter for rows in KP array

    cursor = arcpy.da.InsertCursor(fcKP, ['KP', 'SHAPE@XY'])
    for row in KPlist:
        cursor.insertRow(row)
    del cursor, row
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
