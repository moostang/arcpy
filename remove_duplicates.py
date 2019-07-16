# --------------------------------------- #
# Function to remove duplicate x,y points #
# --------------------------------------- #

def remove_duplicates(xyList):

    i = 0
    k = 0
    n = 0

    keepList = []
    kFinal = len(xyList)
    oneList = xyList

    while len(oneList) > 0: # k <= kFinal or

        ## TEST OUTPUT ##
        print("BEGIN Iteration {0}. Base Index k = {1}".format(n,k))

        # oneList will become empty at the end
        x1 = oneList[i][0]
        y1 = oneList[i][1]

        keepList.append((x1,y1))

        newList = []
        k += 1
        for j in range(i+1, len(oneList)):
            newList.append(oneList[j])

        del j

        xyList = oneList
        oneList = []
        for j in range(len(newList)):
            x2 = newList[j][0]
            y2 = newList[j][1]
            xEval = x1 - x2
            yEval = y1 - y2
            if xEval !=0 and yEval != 0:
                oneList.append(newList[j])

                ## TEST OUTPUT ##
                print("    Iteration {0}. FINAL Compare Index k = {1}. Populating oneList with j = {2}".format(n,k,j))

            else:

                ## TEST OUTPUT ##
                print("  Iteration {0}. Compare Index k = {1} is same. Checking next index k = {2}.".format(n,k-1,k))


        ## TEST OUTPUT ##
        print("      Iteration {0}. END FINAL Compare Index k = {1}.".format(n,k,len(oneList)))

        diff = len(newList) - len(oneList)
        k = k + diff

        ## TEST OUTPUT ##
        print("      Length of oneList = {0}. Difference = {1}".format(len(oneList), diff))

        ## TEST OUTPUT ##
        print("        END Iteration {0}. New Base index k = {1}".format(n,k))

        n +=1

        del j, x2, y2, xEval, yEval

    ## TEST OUTPUT ##
    print("*\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\*")
    print("*\\\\\\\* Duplicates removed. Total number of non-duplicates is {0}.".format(len(keepList)))
    print("*\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\*")

    return keepList
