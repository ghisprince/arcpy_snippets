"""
 Random useful arcpy geometry functions.

"""
import math
import arcpy
import json

def merge_paths_simple(fc):
    """
    Takes each path of a line feature. If made of more than one path
     (aka segment, aka part) connects them into a single path.

     Vertex xy are unchanged.

     Assumption is that path 0 is followed by path 1, then 2, etc...
    """
    import json
    with arcpy.da.UpdateCursor(fc, "Shape@JSON") as uc:
        for row in uc:
            j = json.loads(row[0])
            paths = j['paths']
            if len(paths) > 1:
                j['paths'] = [list(itertools.chain(*paths))]
                uc.updateRow([json.dumps(j),])


def dist(a, b):
    """ distance formula for 2 points """
    return math.hypot(a[0] - b[0], a[1] - b[1])


def merge_paths_2(paths, search_dist=0):
    """
    Merges the paths based on from/to ends and search distance.
    """

    for i1, v1 in enumerate(paths):
        for i2, v2 in enumerate(paths):
            if i1 == i2:
                continue

            if dist(v1[-1], v2[1]) <= search_dist:
                paths[i1] = v1 + v2
                paths.pop(i2)

                return merge_paths_2(paths, search_dist)
    return paths


def merge_paths_logical(fc, search_dist=30):
    """
    Takes each path of a line feature. If made of more than one path
     (aka segment, aka part) connects them into a single path.

     Vertex xy are unchanged.

     Finds downstream path by searching end-point to all start-points within
      search_dist.
    """

    with arcpy.da.UpdateCursor(fc, "Shape@JSON") as uc:
        for row in uc:
            j = json.loads(row[0])
            j['paths'] = merge_paths_2(j['paths'], search_dist)
            uc.updateRow([json.dumps(j),])