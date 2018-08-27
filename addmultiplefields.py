import arcpy

def addmultiplefields(workspace,intable,infields):
    """add multiple fields to table. Innfields must be list with tuples (fieldname,field_type)"""
    
    arcpy.env.workspace = workspace
    for nametype in infields:
        try:
            fieldname,fieldtype = nametype[0],nametype[1]
            arcpy.AddField_management(intable,fieldname,fieldtype)
        except arcpy.ExecuteError as e:
            print(e)
