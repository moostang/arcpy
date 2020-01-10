# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
def calculate_next_coordinates(x1, x2, y1, y2, projectedDistance):

    # Calculate the slope and distance between two Cartesian points. x-axis is
    # along the East-West direction and the y-axis is along the North-South
    # direction. Thus, the difference in x-axis and y-axis between two points
    # is calculated along these axes.
    #
    # Input:
    #   For 2-D maps,
    #       x1,  x-axis value of first cartesian point (FLOAT)
    #       x2,  x-axis value of second cartesian point (FLOAT)
    #       y1,  y-axis value of first cartesian point (FLOAT)
    #       y2,  y-axis value of second cartesian point (FLOAT)
    #       projectedDistance, distance of the new x-y point that lies either
    #            in between the two input points or extended from second point.
    #            If inbetween:
    #                x_new = x1 + delta_x
    #                y_new = y1 + delta_y
    #            else:
    #                x_new = x2 + delta_x
    #                y_new = y2 + delta_y
    #
    #   For 2-D graphs,
    #       x1,  x-axis value of first cartesian point (FLOAT)
    #       x2,  x-axis value of second cartesian point (FLOAT)
    #       y1,  Elevation of first cartesian point (FLOAT)
    #       y2,  Elevation of second cartesian point (FLOAT)
    #       projectedDistance, IGNORED.
    #
    #
    # Output:
    #   For 2-D Maps,
    #   distance, Cartesian Distance between two points. Does not account
    #             for flattenint associated with UTM coordinates. Accuracy
    #             of long distances (> 100 m) may not be trustworthy.
    #             Used as 2-D Chainage distance (may differ from survey
    #             chainage data)
    #   phi,      Bearing (in 2*math.pi) between two points. The north
    #             direction is 0 degrees and counted CLOCKWISE. Used to find
    #             bearing between two points on a flat 2-D map
    #   theta2,   The angle between points on a map, with East direction as
    #             0 degrees and counted COUNTER-CLOCKWISE.
    #
    #   For 2-D graphs/profiles,
    #   slope,    Slope betweewn two points. The horizontal plane is the
    #             plane of origin. Slope above and below the plane are
    #             positive and negative, respectively. This variable is
    #             needed for creating 2-D profiles/graphs.
    #   distance, Cartesian length between two points on a graph/profile.
    #             Used as 3-D Chainage distance (may differ from survey
    #             chainage data)
    #
    # Created: April 24, 2019 (moostang)
    # Modifiede on: April 24, 2019 (moostang)
    #             Filename renamed to calculate_next_coordinates.py from
    #             slope_distance.py


    import math

    numer = y2 - y1 # Numerator
    denom = x2 - x1 # Denominator

    # Calculate geodetic length (straight-line distance) between two points

    #                             x2, y2
    #                                +
    #                              / |
    #                            /   |
    #                          /     |  Delta y
    #                        /       |
    #                      /         |
    #                     +----------+
    #                  x1, y1
    #
    #                     <-Delta x->

    distance = math.sqrt( numer**2 + denom**2)

    # Check if denominator is zero, i.e. both points lies on the same
    # y-axis plane.
    # a. If denominator is zero, then determine if it lies on the
    #    upper (positive) or bottom (negative) y-axis plane.
    # b. If denominator is not zero, then proceed with normal pythagorean
    #    trigonometric calculations
    #

    if denom == 0:
        print("Denominator is zero")
        b = 0 # Delta x
        if y2 > y1:
            print("    and y2 > y1")
            p =  1 # Second point is above first point
            theta = math.pi/2
        elif y2 < y1:
            print("    and y2 < y1")
            p = -1 # Second point is below first point
            theta = - math.pi/2
        else:
            print("    and y2 = y1. Both of them are the same points !")
            p = 0 # Delta x
            b = 0 # Delta y
            theta = 0
    else:
        print("Denominator is NOT zero")
        theta = math.atan(numer/denom)
        p = math.sin(theta)
        b = math.cos(theta)

    # Assign slope, phi, theta2 for different quadrants
    # --------------------------------------------------
    #
    # Slope, phi, theta2 for the 1st quadrant
    slope  = theta
    phi    = math.pi/2 - theta
    theta2 = theta
    #print("Original slope is " + str(slope*(180/math.pi)))

    # Slope, phi, and theta2 for other quadrants
    if x2 < x1:
        # Slope, phi, and theta2 for 2nd and 3rd quadrants, ie. on the left side.

        slope  = - theta
        phi    = 3*math.pi/2 - theta
        theta2 = math.pi + theta

        #print("   Corrected slope is " + str(slope*(180/math.pi)))

    if x2 >= x1 and y2 < y1:
        # Slope, phi, and theta2 for 4th quadrant only, i.e. bottom-right side.

        phi    = math.pi/2 - theta
        theta2 = 2*math.pi + theta

    # Calculate x-y coordinates for new point
    if denom != 0:

        # If projecte distance != 0
        delta_x = math.cos(theta2)*projectedDistance
        delta_y = math.sin(theta2)*projectedDistance
    else:

        # If projected distance = 0
        delta_x = b*projectedDistance
        delta_y = p*projectedDistance

    return slope, distance, phi, theta2, delta_x, delta_y

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
