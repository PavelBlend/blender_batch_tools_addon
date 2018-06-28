bl_info = {'name'        : 'Batch Tools',
           'author'      : 'Pavel_Blend',
           'version'     : (0, 0, 1),
           'blender'     : (2, 71, 0),
           'location'    : '\'Batch Tools\' Panels',
           'description' : 'Edit Settings in many objects.',
           'category'    : '3D View'}


import bpy, random
from bpy.props import (BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       FloatVectorProperty)


def is_prefix(ext):
    try:
        int(ext)
        is_prefix = True
    except:
        is_prefix = False
    return is_prefix


def numerate_data():
    b = bpy.data
    for data in (b.objects, b.meshes, b.materials, b.textures):
        n = 0
        for n, x in enumerate(data):
            x.name = '{0:0>4}'.format(n)


def rename_objects():
    for ob in bpy.data.objects:
        if len(ob.material_slots):
            mat = ob.material_slots[0].material
            if mat.texture_slots[0]:
                tex = mat.texture_slots[0].texture
                if tex.type == 'IMAGE':
                    if tex.image:
                        image = tex.image.name
                        image_ext = image.split('.')[-1]
                        if is_prefix(image_ext):
                            image_ext = '.' + image.split('.')[-2] + image.split('.')[-1]
                        image_name = image[0 : -(len(image_ext) + 1)]
                        ob.name = image_name
                        ob.data.name = image_name + '_mesh'


def reneme_materials():
    for ob in bpy.data.objects:
        for mat_slot in ob.material_slots:
            material = mat_slot.material
            try:
                image = material.texture_slots[0].texture.image.name
                image_ext = image.split('.')[-1]
                if is_prefix(image_ext):
                    image_ext = '.' + image.split('.')[-2] + image.split('.')[-1]
                image_name = image[0 : -(len(image_ext) + 1)]
                material.name = image_name
            except:
                pass


def reneme_textures():
    for ob in bpy.data.objects:
        for mat_slot in ob.material_slots:
            material = mat_slot.material
            try:
                image = material.texture_slots[0].texture.image.name
                image_ext = image.split('.')[-1]
                if is_prefix(image_ext):
                    image_ext = '.' + image.split('.')[-2] + image.split('.')[-1]
                image_name = image[0 : -(len(image_ext) + 1)]
                material.texture_slots[0].texture.name = image_name
            except:
                pass


def remove_not_use_materials():
    for mat in bpy.data.materials:
        if mat.users == 0:
            bpy.data.materials.remove(mat)
    bpy.context.scene.update()


def remove_doubles(objects, distance):
    out = ''
    for ob in objects:
        name = ob.name
        if ob.type == 'MESH':
            bpy.context.scene.objects.active = ob
            vCnt = len(ob.data.vertices)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=distance)
            bpy.ops.object.mode_set(mode='OBJECT')
            vCntAfter = len(ob.data.vertices)
            if vCnt - vCntAfter != 0:
                out += '{: <20} remove vertices: {}\n'.format(name, vCnt - vCntAfter)
    print(out)


def check_invalid():
    haveInvalid = False
    for ob in bpy.context.selected_objects:
        name = ob.name
        if ob.type == 'MESH':
            bpy.context.scene.objects.active = ob
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            invalidFace = []
            for face in ob.data.polygons:
                if face.area <= 0.000005:
                    invalidFace.append(face.index)
            if len(invalidFace):
                haveInvalid = True
                for index in invalidFace:
                    ob.data.polygons[index].select = True
                print('{: <32} - invalid face count: {}'.format(name, len(invalidFace)))
    if not haveInvalid:
        print('Meshes not have invalid face.')


def createMatList():
    scn = bpy.context.scene
    MatList = []
    if scn.EditData == 'SCENE':
        for mat in bpy.data.materials:
            MatList.append(mat)
    elif scn.EditData == 'SELECT':
        for ob in bpy.context.selected_objects:
            for slot in ob.material_slots:
                MatList.append(slot.material)
    elif scn.EditData == 'ACTIVE':
        for slot in bpy.context.object.material_slots:
            MatList.append(slot.material)
    return MatList


def createTexList():
    scn = bpy.context.scene
    TexList = []
    if scn.EditData == 'SCENE':
        for ob in bpy.data.objects:
            for matSlot in ob.material_slots:
                for texSlot in matSlot.material.texture_slots:
                    if texSlot:
                        TexList.append(texSlot)
    elif scn.EditData == 'SELECT':
        for ob in bpy.context.selected_objects:
            for matSlot in ob.material_slots:
                for texSlot in matSlot.material.texture_slots:
                    if texSlot:
                        TexList.append(texSlot)
    elif scn.EditData == 'ACTIVE':
        for matSlot in bpy.context.object.material_slots:
            for texSlot in matSlot.material.texture_slots:
                if texSlot:
                    TexList.append(texSlot)
    return TexList


def createMeshList():
    scn = bpy.context.scene
    MeshList = []
    if scn.EditData == 'SCENE':
        for mesh in bpy.data.meshes:
            MeshList.append(mesh)
    elif scn.EditData == 'SELECT':
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH':
                mesh = ob.data
                MeshList.append(mesh)
    elif scn.EditData == 'ACTIVE':
        ob = bpy.context.object
        if ob.type == 'MESH':
            MeshList.append(ob.data)
    return MeshList


def createArmList():
    scn = bpy.context.scene
    armList = []
    if scn.EditData == 'SCENE':
        for arm in bpy.data.armatures:
            armList.append(arm)
    elif scn.EditData == 'SELECT':
        for ob in bpy.context.selected_objects:
            if ob.type == 'ARMATURE':
                armList.append(ob.data)
    elif scn.EditData == 'ACTIVE':
        ob = bpy.context.object
        if ob.type == 'ARMATURE':
            armList.append(ob.data)
    return armList


def edit_diffuse_color(self, context):
    scn = context.scene
    if scn.EditMat:
        MatList = createMatList()
        for mat in MatList:
            mat.diffuse_color = scn.DifColor
    return None


def edit_diffuse_intensity(self, context):
    scn = context.scene
    if scn.EditMat:
        MatList = createMatList()
        for mat in MatList:
            mat.diffuse_intensity = scn.DifInt
    return None


def edit_specular_color(self, context):
    scn = context.scene
    if scn.EditMat:
        MatList = createMatList()
        for mat in MatList:
            mat.specular_color = scn.SpecColor
    return None


def edit_specular_intensity(self, context):
    scn = context.scene
    if scn.EditMat:
        MatList = createMatList()
        for mat in MatList:
            mat.specular_intensity = scn.SpecInt
    return None


def edit_specular_hardness(self, context):
    scn = context.scene
    if scn.EditMat:
        MatList = createMatList()
        for mat in MatList:
            mat.specular_hardness = scn.SpecHard
    return None


def edit_emit(self, context):
    scn = context.scene
    if scn.EditMat:
        MatList = createMatList()
        for mat in MatList:
            mat.emit = scn.Emit
    return None


def edit_shadeless(self, context):
    scn = context.scene
    if scn.EditMat:
        MatList = createMatList()
        for mat in MatList:
            mat.use_shadeless = scn.Shadeless
    return None


def edit_transparency(self, context):
    scn = context.scene
    if scn.EditMat:
        MatList = createMatList()
        for mat in MatList:
            mat.use_transparency = scn.Transperency
    return None


def edit_transparency_method(self, context):
    scn = context.scene
    if scn.EditMat and scn.Transperency:
        MatList = createMatList()
        for mat in MatList:
            mat.transparency_method = scn.TransperencyMethod
    return None


def edit_alpha(self, context):
    scn = context.scene
    if scn.EditMat and scn.Transperency:
        MatList = createMatList()
        for mat in MatList:
            mat.alpha = scn.Alpha
    return None


def edit_show_weight(self, context):
    scn = context.scene
    if scn.EditMesh:
        MeshList = createMeshList()
        for mesh in MeshList:
            mesh.show_weight = context.scene.ShowWeight
    return None


def edit_double_sided(self, context):
    scn = context.scene
    if scn.EditMesh:
        MeshList = createMeshList()
        for mesh in MeshList:
            mesh.show_double_sided = context.scene.DoubleSided
    return None


def edit_draw_type(self, context):
    if context.scene.EditArm:
        armList = createArmList()
        for arm in armList:
            arm.draw_type = context.scene.ArmDrawType


def edit_armature_axes(self, context):
    if context.scene.EditArm:
        armList = createArmList()
        for arm in armList:
            arm.show_axes = context.scene.ArmAxes


def edit_texture_coordinates(self, context):
    if context.scene.EditTex:
        texList = createTexList()
        for tex in texList:
            tex.texture_coords = context.scene.TexCoord
    return None


def edit_texture_diffuse(self, context):
    if context.scene.EditTex:
        texList = createTexList()
        for tex in texList:
            tex.use_map_color_diffuse = context.scene.TexUseDiff
    return None


def edit_texture_diffuse_factor(self, context):
    if context.scene.EditTex:
        texList = createTexList()
        for tex in texList:
            tex.diffuse_color_factor = context.scene.TexDiff
    return None


def edit_texture_alpha(self, context):
    if context.scene.EditTex:
        texList = createTexList()
        for tex in texList:
            tex.use_map_alpha = context.scene.TexUseAlpha
    return None


def edit_texture_alpha_factor(self, context):
    if context.scene.EditTex:
        texList = createTexList()
        for tex in texList:
            tex.alpha_factor = context.scene.TexAlpha
    return None


def remove_not_used_material_slots(bpy_object):
    use_material_slots = set()
    for face in bpy_object.data.polygons:
        use_material_slots.add(face.material_index)
    all_material_slots = set(range(len(bpy_object.material_slots)))
    delete_material_slots = all_material_slots - use_material_slots
    delete_material_slots = list(delete_material_slots)
    delete_material_slots.sort()
    delete_material_slots.reverse()
    for material_index in delete_material_slots:
        bpy_object.active_material_index = material_index
        bpy.ops.object.material_slot_remove()


s = bpy.types.Scene
s.EditData = EnumProperty(items=[
                         ('SCENE', 'Scene', ''),
                         ('SELECT', 'Select', ''),
                         ('ACTIVE', 'Active', '')],
                         default='SCENE',
                         name='Edit')
# material diffuse
s.DifColor = FloatVectorProperty(name='Color',
                                 default=(1.0, 1.0, 1.0),
                                 min=0,
                                 max=1,
                                 subtype='COLOR',
                                 size=3,
                                 precision=6,
                                 step=0.1,
                                 update=edit_diffuse_color)
s.DifInt = FloatProperty(name='Intensity',
                         default=1,
                         min=0,
                         max=1,
                         subtype='FACTOR',
                         update=edit_diffuse_intensity)
# material specular
s.SpecColor = FloatVectorProperty(name='Specular',
                                  default=(1.0, 1.0, 1.0),
                                  min=0,
                                  max=1,
                                  subtype='COLOR',
                                  size=3,
                                  precision=6,
                                  step=0.1,
                                  update=edit_specular_color)
s.SpecInt = FloatProperty(name='Intensity',
                          default=0.5,
                          min=0,
                          max=1,
                          subtype='FACTOR',
                          update=edit_specular_intensity)
s.SpecHard = IntProperty(name='Hardness',
                         default=50,
                         min=1,
                         max=511,
                         update=edit_specular_hardness)
# material shading
s.Emit = FloatProperty(name='Emit',
                       default=0.0,
                       min=0,
                       max=2,
                       update=edit_emit)
s.Shadeless = BoolProperty(name='Shadeless',
                           default=False,
                           update=edit_shadeless)
# material alpha
s.Transperency = BoolProperty(name='Use',
                              default=False,
                              update=edit_transparency)
s.TransperencyMethod = EnumProperty(items=[
                                    ('MASK', 'Mask', ''),
                                    ('Z_TRANSPARENCY', 'Z Transperency', ''),
                                    ('RAYTRACE', 'Raytrace', '')],
                                    default='Z_TRANSPARENCY',
                                    name='Method',
                                    update=edit_transparency_method)
s.Alpha = FloatProperty(name='Alpha',
                        default=1,
                        min=0,
                        max=1,
                        subtype='FACTOR',
                        update=edit_alpha)
# texture
s.TexUseDiff = BoolProperty(name='Use Alpha',
                            update=edit_texture_diffuse)
s.TexDiff = FloatProperty(name='Color',
                          default=1,
                          min=-1,
                          max=1,
                          subtype='FACTOR',
                          update=edit_texture_diffuse_factor)
s.TexUseAlpha = BoolProperty(name='Use Alpha',
                             update=edit_texture_alpha)
s.TexAlpha = FloatProperty(name='Alpha',
                           default=1,
                           min=-1,
                           max=1,
                           subtype='FACTOR',
                           update=edit_texture_alpha_factor)
s.TexCoord = EnumProperty(items=[
                          ('UV', 'UV', ''),
                          ('ORCO', 'Generate', ''),
                          ('OBJECT', 'Object', ''),
                          ('GLOBAL', 'Global', '')],
                          name='Coordinates',
                          update=edit_texture_coordinates)
# mesh
s.ShowWeight = BoolProperty(name='Show Weights',
                            update=edit_show_weight)
s.DoubleSided = BoolProperty(name='Double Sided',
                             update=edit_double_sided)
# armature
s.ArmDrawType = EnumProperty(items=[
                            ('OCTAHEDRAL', 'Octahedral', ''),
                            ('STICK', 'Stick', ''),
                            ('BBONE', 'B-Bone', ''),
                            ('ENVELOPE', 'Envelope', ''),
                            ('WIRE', 'Wire', '')],
                            name='Draw Type',
                            update=edit_draw_type)
s.ArmAxes = BoolProperty(name='Axes',
                         update=edit_armature_axes)
# Tools
s.WeldDist = FloatProperty(name='Weld Distance',
                           default=0.0001,
                           min=0,
                           max=1)
s.EditMat = BoolProperty(name='Edit Material', default=False)
s.EditMesh = BoolProperty(name='Edit Mesh', default=False)
s.EditArm = BoolProperty(name='Edit Armature', default=False)
s.EditTex = BoolProperty(name='Edit Texture', default=False)


class BT_RandomColor(bpy.types.Operator):
    bl_idname = 'batch.rand_clr'
    bl_label = 'Randomize Material Color (batch tools)'

    def execute(self, context):
        scn = context.scene
        if scn.EditMat:
            MatList = createMatList()
            for mat in MatList:
                mat.diffuse_color = ((random.random(),
                                    random.random(),
                                    random.random()))
        return{'FINISHED'}


class BT_MatPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'
    bl_label = 'Batch Tools'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scn = bpy.context.scene
        self.layout.prop(scn, 'EditMat', text='')

    def draw(self, context):
        scn = context.scene
        l = self.layout
        col = l.column()
        col.active = scn.EditMat

        col.label('Diffuse:')
        row = col.row()
        row.prop(scn, 'DifColor', text='')
        row.operator('batch.rand_clr', text='Randomize Color')
        col.prop(scn, 'DifInt')

        col.label('Specular:')
        col.prop(scn, 'SpecColor', text='')
        col.prop(scn, 'SpecInt')
        col.prop(scn, 'SpecHard')

        col.label('Shading:')
        row = col.row()
        row.prop(scn, 'Emit')
        row.prop(scn, 'Shadeless')

        col.label('Transperency:')
        col.prop(scn, 'Transperency')
        row = col.row()
        row.active = scn.Transperency
        row.prop(scn, 'TransperencyMethod', expand=True)
        col1 = col.column()
        col1.active = scn.Transperency
        col1.prop(scn, 'Alpha')


class BT_MeshPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_label = 'Batch Tools'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mesh

    def draw_header(self, context):
        scn = bpy.context.scene
        self.layout.prop(scn, 'EditMesh', text='')

    def draw(self, context):
        scn = context.scene
        l = self.layout
        row = l.row()
        row.active = scn.EditMesh
        row.prop(scn, 'ShowWeight')
        row.prop(scn, 'DoubleSided')


class BT_ArmPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_label = 'Batch Tools'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.armature

    def draw_header(self, context):
        scn = bpy.context.scene
        self.layout.prop(scn, 'EditArm', text='')

    def draw(self, context):
        scn = context.scene
        l = self.layout
        row = l.row()
        row.active = scn.EditArm
        col = row.column()
        col.prop(scn, 'ArmAxes')
        row = col.row()
        row.prop(scn, 'ArmDrawType', expand=True)


class BT_TexPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'texture'
    bl_label = 'Batch Tools'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scn = bpy.context.scene
        self.layout.prop(scn, 'EditTex', text='')

    def draw(self, context):
        scn = context.scene

        def factor_but(layout, toggle, factor, name):
            row = layout.row(align=True)
            row.prop(scn, toggle, text='')
            sub = row.row(align=True)
            sub.active = getattr(scn, toggle)
            sub.prop(scn, factor, text=name, slider=True)
            return sub

        l = self.layout
        col = l.column()
        col.active = scn.EditTex
        col.prop(scn, 'TexCoord')
        col = col.column()
        factor_but(col, 'TexUseDiff', 'TexDiff', 'Color')
        factor_but(col, 'TexUseAlpha', 'TexAlpha', 'Alpha')


class BT_RenamePanel(bpy.types.Panel):
    bl_category = 'Batch Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Rename'

    def draw(self, context):
        l = self.layout
        l.label('Name as Image Name')
        l.operator('batch_tools.rename_objects', text='Objects and Meshes')
        l.operator('batch_tools.rename_materials', text='Materials')
        l.operator('batch_tools.rename_textures', text='Textures')
        l.label('Batch Rename')
        l.operator('batch_tools.numerate', text='Numerate Data')


class BT_UtilsPanel(bpy.types.Panel):
    bl_category = 'Batch Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Utils'

    def draw(self, context):
        scn = bpy.context.scene
        l = self.layout
        l.label('Remove')
        l.operator('batch_tools.remove_not_use_mat', text='Not Use Materials')
        l.operator('batch_tools.rem_not_used_mat_slots', text='Not Use Material Slots')
        l.prop(scn, 'EditData')
        l.prop(scn, 'WeldDist')
        l.operator('batch_tools.remove_doubles', text='Double Vertices')
        l.operator('batch_tools.check_invalid', text='Check Invalid')


class BT_NumerateData(bpy.types.Operator):
    bl_idname = 'batch_tools.numerate'
    bl_label = 'Numerate (batch tools)'

    def execute(self, context):
        numerate_data()
        return{'FINISHED'}    


class BT_RenameObj(bpy.types.Operator):
    bl_idname = 'batch_tools.rename_objects'
    bl_label = 'Rename Objects (batch tools)'

    def execute(self, context):
        rename_objects()
        return{'FINISHED'}


class BT_RenameMat(bpy.types.Operator):
    bl_idname = 'batch_tools.rename_materials'
    bl_label = 'Settings Textures (batch tools)'

    def execute(self, context):
        reneme_materials()
        return{'FINISHED'}


class BT_RenameTex(bpy.types.Operator):
    bl_idname = 'batch_tools.rename_textures'
    bl_label = 'Settings Textures (batch tools)'

    def execute(self, context):
        reneme_textures()
        return{'FINISHED'}


class BT_RemoveNotUseMat(bpy.types.Operator):
    bl_idname = 'batch_tools.remove_not_use_mat'
    bl_label = 'Remove Not Use Materials (batch tools)'

    def execute(self, context):
        remove_not_use_materials()
        return{'FINISHED'}


class BT_RemoveDoubleVerts(bpy.types.Operator):
    bl_idname = 'batch_tools.remove_doubles'
    bl_label = 'Remove Double Vertices (batch tools)'

    def execute(self, context):
        scn = context.scene
        objects = []
        if scn.EditData == 'SELECT':
            objects = bpy.context.selected_objects
        elif scn.EditData == 'ACTIVE':
            if bpy.context.object:
                objects = (bpy.context.object,)
        elif scn.EditData == 'SCENE':
            objects = bpy.context.scene.objects
        if len(objects):
            remove_doubles(objects, scn.WeldDist)
        return{'FINISHED'}


class BT_CheckInvalid(bpy.types.Operator):
    bl_idname = 'batch_tools.check_invalid'
    bl_label = 'Check Invalid Face (Area=0) (batch tools)'

    def execute(self, context):
        check_invalid()
        return{'FINISHED'}


class BT_RemoveNotUsedMaterialSlots(bpy.types.Operator):
    bl_idname = 'batch_tools.rem_not_used_mat_slots'
    bl_label = 'Remove not used material slots (batch tools)'

    def execute(self, context):
        edit_obj = context.scene.EditData
        object_list = []
        if edit_obj == 'ACTIVE':
            if context.object.type == 'MESH':
                object_list.append(context.object)
        elif edit_obj == 'SELECT':
            for object in context.selected_objects:
                if object.type == 'MESH':
                    object_list.append(object)
        elif edit_obj == 'SCENE':
            for object in context.scene.objects:
                if object.type == 'MESH':
                    object_list.append(object)
        active_object = context.scene.objects.active
        for object in object_list:
            context.scene.objects.active = object
            remove_not_used_material_slots(object)
        context.scene.objects.active = active_object
        return{'FINISHED'}


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == '__main__':
    register()

