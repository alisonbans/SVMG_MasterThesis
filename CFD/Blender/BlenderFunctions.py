import bpy
import os
def artery_to_surface(stl_path = "C:/Users/z5713258/SVMG_MasterThesis/CFD/FEA_Results/BalloonArteryCriExp3Nov.stl"):
    print('1')
    if not bpy.context.active_object is None :
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)


    # Import the STL file
    bpy.ops.import_mesh.stl(filepath=stl_path)

    # Get the imported object (assumes it’s the last selected object)
    obj = bpy.context.selected_objects[0]

    # Make it active and selected
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    #Go into editing mode
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
    bpy.ops.mesh.select_all(action='DESELECT')

    #Delete balloon and crimping surface
    bpy.ops.mesh.select_linked_pick(deselect=False, delimit={'SEAM'}, object_index=0, index=2049942)
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.mesh.select_linked_pick(deselect=False, delimit={'SEAM'}, object_index=0, index=2129508)
    bpy.ops.mesh.delete(type='FACE')

    # Separate the artery and the stent and rename them independently
    bpy.ops.mesh.select_linked_pick(deselect=False, delimit={'SEAM'}, object_index=0, index=1532902)
    bpy.ops.mesh.separate(type='SELECTED')
    bpy.context.active_object.name = "STENT"
    for obj in bpy.context.selected_objects:
        if obj != bpy.context.active_object:
            obj.name = "STENTED"


    # Delete artery extermities
    for face_index in [281433, 23899]:
        bpy.ops.object.mode_set(mode='OBJECT')
        artery = bpy.data.objects["STENTED"]
        bpy.context.view_layer.objects.active = artery
        obj.select_set(True)
        for poly in obj.data.polygons:
            poly.select = False
        obj.data.polygons[face_index].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="FACE")
        bpy.ops.mesh.select_similar(type='FACE_COPLANAR', threshold=0.01)
        bpy.ops.mesh.delete(type='FACE')
        
    bpy.ops.mesh.select_linked_pick(deselect=False, delimit={'SEAM'}, object_index=0, index=735850)
    bpy.ops.mesh.delete(type='FACE')
def artery_elongation():
    print('2')
    artery = bpy.data.objects["STENTED"]
    bpy.context.view_layer.objects.active = artery
    artery.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(
        plane_co=(0, 0, 2.0),   # Z = 2.0, XY plane parallel
        plane_no=(0, 0, 1),     # Normal along Z
        xstart=0, xend=1000,    # Dummy viewport coords
        ystart=0, yend=1000,
        flip=False,
        use_fill=False
    )
    bpy.ops.mesh.loop_to_region()
    bpy.ops.mesh.separate(type='SELECTED')
    obj = bpy.data.objects["STENTED.001"]
    obj.name = "PROXIMAL"

    artery = bpy.data.objects["STENTED"]
    bpy.context.view_layer.objects.active = artery
    artery.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(
        plane_co=(0, 0,20.0),   # Z = 2.0, XY plane parallel
        plane_no=(0, 0, 1),     # Normal along Z
        xstart=0, xend=1000,    # Dummy viewport coords
        ystart=0, yend=1000,
        flip=False,
        use_fill=False
    )
    bpy.ops.mesh.loop_to_region()
    bpy.ops.mesh.separate(type='SELECTED')
    obj = bpy.data.objects["STENTED.001"]
    obj.name = "DISTAL"

    edges_to_extrude = [
    ("DISTAL", 33963, 12, "DISTAL_EXT", ">"),    # Faces above z_target
    ("PROXIMAL", 37596, -12, "PROXIMAL_EXT", "<")  # Faces below z_target
    ]

    tol = 1e-5
    for obj_name, edge_index, z_extrude, new_obj_name, comparison in edges_to_extrude:
        # Deselect all objects
        for obj in bpy.context.selected_objects:
            obj.select_set(False)

        obj = bpy.data.objects[obj_name]
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Go to Edit Mode and Edge Selection
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.select_all(action='DESELECT')

        # Switch to Object Mode to select starting edge
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.data.edges[edge_index].select = True

        # Back to Edit Mode and select similar connected edges
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_similar(type='EDGE_FACES', threshold=0.01)

        # Filter edges to only those in the same Z plane
        bpy.ops.object.mode_set(mode='OBJECT')
        v1, v2 = obj.data.edges[edge_index].vertices
        z_target = (obj.data.vertices[v1].co.z + obj.data.vertices[v2].co.z) / 2
        threshold = 1e-5

        for edge in obj.data.edges:
            if edge.select:
                v1, v2 = edge.vertices
                z_avg = (obj.data.vertices[v1].co.z + obj.data.vertices[v2].co.z) / 2
                if abs(z_avg - z_target) > threshold:
                    edge.select = False

        # Back to Edit Mode and extrude along Z
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate={"value": (0, 0, z_extrude)}
        )

        # Switch to Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        tolerance = 1e-5

        for f in obj.data.polygons:
            z_avg = sum(obj.data.vertices[v].co.z for v in f.vertices) / len(f.vertices)
            
            if obj_name == "DISTAL":
                # Select faces created by extrusion
                if z_target - tolerance <= z_avg <= z_target + z_extrude + tolerance:
                    f.select = True
                else:
                    f.select = False
            elif obj_name == "PROXIMAL":
                if comparison == "<" and z_avg < z_target - tol:
                    f.select = True
        # Separate selected faces into a new object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')

        # Rename the new object
        new_obj = [o for o in bpy.context.selected_objects if o.name != obj.name][0]
        new_obj.name = new_obj_name
def select_and_fill_loop(obj_name, edge_index, new_obj_name):
    print('3')
    obj = bpy.data.objects[obj_name]
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Switch to Edit Mode and Edge Select Mode
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.select_all(action='DESELECT')

    # Switch to Object Mode to select the reference edge
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.edges[edge_index].select = True

    # Get the Z position of the reference edge
    v1, v2 = obj.data.edges[edge_index].vertices
    z_target = (obj.data.vertices[v1].co.z + obj.data.vertices[v2].co.z) / 2
    threshold = 1e-5

    # Select all edges in the same Z plane
    for edge in obj.data.edges:
        v1, v2 = edge.vertices
        z_avg = (obj.data.vertices[v1].co.z + obj.data.vertices[v2].co.z) / 2
        if abs(z_avg - z_target) < threshold:
            edge.select = True
        else:
            edge.select = False

    # Back to Edit Mode and fill the loop
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.edge_face_add()
    
    # Store current object names
    existing_names = set(o.name for o in bpy.data.objects)

    bpy.ops.mesh.separate(type='SELECTED')
    bpy.ops.object.mode_set(mode='OBJECT')
    new_obj = next(o for o in bpy.data.objects if o.name not in existing_names)
    new_obj.name = new_obj_name
    #bpy.ops.mesh.edge_face_add()
    #bpy.ops.object.mode_set(mode='OBJECT')
def export(case = 'NUS19_SW60_ST60'):
    # Set your export directory
    export_dir = "C:/Users/z5713258/SVMG_MasterThesis/CFD/CFD_STL_input"
    case_dir = os.path.join(export_dir, case)
    # Create the directory if it doesn't exist
    if not os.path.exists(case_dir):
        os.makedirs(case_dir)
    
    # Deselect everything first
    bpy.ops.object.select_all(action='DESELECT')

    # Loop through all mesh objects in the scene
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            # Select and activate the object
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            # Define export path
            export_path = os.path.join(case_dir, f"{obj.name}.stl")

            # Export as ASCII STL
            bpy.ops.export_mesh.stl(
                filepath=export_path,
                use_selection=True,
                ascii=True,
                use_mesh_modifiers=True,
                global_scale=1.0,
                axis_forward='-Z',
                axis_up='Y'
            )

            # Deselect the object after export
            obj.select_set(False)

def main():
    artery_to_surface()
    artery_elongation()
    select_and_fill_loop("PROXIMAL_EXT", 344, "INLET")
    select_and_fill_loop("DISTAL_EXT", 311, "OUTLET")
    export()

if __name__ == "__main__":
    main()
