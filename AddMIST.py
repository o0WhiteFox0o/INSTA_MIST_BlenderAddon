# To make this add-on installable, create an extension with it:
# https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html

import bpy # cổng truy cập vào Blender

from bpy.types import Panel, Operator
# Panel - Tạo bảng giao diện (UI Panel)
# Operator - Tạo hành động (nút bấm, lệnh) 


def mist_comp_action(context):
    # cau truc quan ly Node trong Compositing
    tree = context.scene.node_tree
    
    # dieu khien note -> tree.nodes.get('')
    comp_node = tree.nodes.get('Composite') # ten node duoc lay tu bien Name cua note 
    comp_node.location = (700,0)
    
    render_layer_node = tree.nodes.get('Render Layers')
    render_layer_node.location = (-200, 0)
    
   
    # tao note moi -> tree.nodes.new('')
    viewer_node = tree.nodes.new('CompositorNodeViewer')
    viewer_node.location = (700, 200)
    
    mix_node = tree.nodes.new('CompositorNodeMixRGB') # node Mix - CompositorNodeMixRGB
    mix_node.location = (500, 0)
    mix_node.blend_type = 'ADD'
    mix_node.use_clamp = True
    
    mix2_node = tree.nodes.new('CompositorNodeMixRGB') # CompositorNodeMixRGB
    mix2_node.location = (300,0)
    mix2_node.blend_type = 'MULTIPLY'
    mix2_node.use_clamp = True


    cr_node = tree.nodes.new('CompositorNodeValToRGB') # node Color Ramp
    cr_node.location = (100,400)
    cr_node.color_ramp.elements[0].color = (0.2, 0.2, 0.2, 1)
    cr_node.color_ramp.elements.new(position = 0.27)
    
    # tao lien ket gia cac node
    link = tree.links.new
    
    link(mix_node.outputs[0], viewer_node.inputs[0])
    link(mix_node.outputs[0], comp_node.inputs[0])
    link(mix2_node.outputs[0], mix_node.inputs[1])
    link(cr_node.outputs[0], mix2_node.inputs[1])
    link(render_layer_node.outputs[0], mix_node.inputs[2])
    link(render_layer_node.outputs[3], cr_node.inputs[0])
    
    return {'FINISHED'}


# Khai báo một panel UI mới
class INSTA_MIST_PT_main_panel(Panel):
    bl_label = "INSTA_MIST (By Sonny)"
    bl_idname = "INSTA_MIST_PT_main_panel"
    bl_space_type = 'VIEW_3D' # Panel xuất hiện ở 3D Viewport
    bl_region_type = 'UI' # Panel nằm ở Sidebar (phím N)
    bl_category = "INSTA-MIST"
 
    # Hàm vẽ UI
    def draw(self, context):
        # Tao bien tham chieu
        layout = self.layout
        scene = context.scene
        world = scene.world.mist_settings # <- coi o dau tra ra cai lenh nay?
        
        layout.prop(world, "start")
        layout.prop(world, "depth")
        layout.prop(world, "falloff")
        # Khi click → gọi Operator có idname tương ứng -> instamist.add_mist_operator
        layout.operator("instamist.add_mist_operator") 
 
# Tạo Operator (Hành động) 
class INSTA_MIST_OT_add_mist(Operator):
    bl_label = "Enable/Disable Mist"
    bl_idname = "instamist.add_mist_operator"
    # Hàm chạy khi nút được bấm
    def execute(self, context):
        scene = context.scene
        camera = bpy.data.cameras['Camera']
        vl= scene.view_layers["ViewLayer"]
        
        if vl.use_pass_mist == False:
            vl.use_pass_mist = True
            camera.show_mist = True
            if scene.use_nodes == False:
                scene.use_nodes = True
            mist_comp_action(context)

        else:
            vl.use_pass_mist = False
            camera.show_mist = False
            tree = context.scene.node_tree
            # tra trang thai
            mix1 = tree.nodes.remove(tree.nodes.get('Mix'))
            mix2 = tree.nodes.remove(tree.nodes.get('Mix.001'))
            #cr = tree.nodes.remove(tree.nodes.get('ColorRamp'))
            cr = None
            for node in tree.nodes:
                if node.type == 'VALTORGB':  # ColorRamp
                    cr = node
                    break
            tree.nodes.remove(cr)
            
            comp_node = tree.nodes.get('Composite')
            viewer_node = tree.nodes.get('Viewer')
            render_layer_node = tree.nodes.get('Render Layers')
            
            tree.links.new(render_layer_node.outputs[0], comp_node.inputs[0])
            tree.links.new(render_layer_node.outputs[0], viewer_node.inputs[0])
            
            
        return {'FINISHED'}
    
 
 
classes = [INSTA_MIST_PT_main_panel, INSTA_MIST_OT_add_mist]
 
 
 # Đăng ký addon với Blender
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
 # Gỡ addon khỏi Blender
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
 
 # Cho phép: chạy script trực tiếp trong Text Editor -> không cần cài addon
if __name__ == "__main__":
    register()