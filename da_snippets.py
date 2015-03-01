"""
 Random useful arcpy data access code snippets.

  ArcGIS 10.x (python 2) and ArcGIS Pro (python 3) compatible

"""
import math
import arcpy
import json
import csv
import os
import io
import sys

PY2 = sys.version_info.major < 3

def fc_geom_to_csv(fc, out_csv):
    """
    Export each vert in a line or poly fc to a csv with OID
    user requested at http://arcpy.wordpress.com/about/#comment-348

    example

        import da_snippets
        da_snippets.export_fc_to_csv(r"c:\proj\fc1.shp", r"c:\proj\fc1.csv")

    output csv looks like this

        1,56019.99998067904,69118.00001450378
        1,56159.99998080942,69026.0000144181
        1,56359.999980995686,68913.00001431286
        2,34985.00002508866,68936.00001433428
        2,35178.000025268404,68805.00001421227

    """
    if PY2:
        csvfile = open(out_csv, "wb", )
    else:
        csvfile = io.open(out_csv, "w", newline="")

    csvwriter = csv.writer(csvfile)
    geomType = arcpy.Describe(fc)
    with arcpy.da.SearchCursor(fc,
                               field_names=("OID@", "SHAPE@JSON")) as cur:
        for row in cur:
            geom = json.loads(row[1])
            if "x" in geom:
                csvwriter.writerow([row[0], geom["x"], geom["y"]] )

            else:
                k = 'paths' if 'paths' in geom else 'rings'
                for path in geom[k]:
                    for pt in path:
                        csvwriter.writerow([row[0]] + pt)

def csv_xy_to_fc(in_csv, fc, fields=(("val", "TEXT"),) ):
    """
    Convert csv containing x,y,val into a gdb point fc.

    example

        import da_snippets
        da_snippets.csv_xy_to_fc(r"c:\proj\fc1.shp", r"c:\proj\fc1.csv")

    """
    sr = arcpy.SpatialReference("WGS 1984")
    arcpy.env.overwriteOutput = True
    fc = arcpy.management.CreateFeatureclass(*os.path.split(fc),
                                             geometry_type="POINT",
                                             spatial_reference=sr)

    for fname, ftype in fields:
        arcpy.AddField_management(fc, fname, ftype)

    with io.open(in_csv, 'r') as csvfile:
        csvreader = csv.reader(csvfile)

        with arcpy.da.InsertCursor(fc, field_names = (["SHAPE@XY"] +
                                           [i[0] for i in fields]) ) as cur:
            for row in csvreader:
                pt = (float(row[0]), float(row[0]),)
                cur.insertRow( [pt,] + row[2:] )


if __name__ == "__main__":
    csv_xy_to_fc("data.csv", "output.shp",
                                 (("val1", "TEXT"), ("val2", "TEXT")))
