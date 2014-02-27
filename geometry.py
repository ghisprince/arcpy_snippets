"""
 Random useful arcpy geometry functions.

"""


def connect_parts(fc):
    """
    Takes each part of a line feature. If made of more than one path 
     (aka segment, aka part) connects them into a single path.
     Vertices are unchanged.
    """
    with arcpy.da.UpdateCursor("lyr", "Shape@JSON") as uc:
        for row in uc:
            j = json.loads(row[0])
            paths = j['paths']
            if len(paths) > 1:
                j['paths'] = [list(itertools.chain(*paths))]
                uc.updateRow([json.dumps(j),])
