from drawioedit import DrawIOEdit
import os

base_path=os.path.dirname(os.path.realpath(__file__))

drawing=DrawIOEdit(file_path=f'{base_path}/test.drawio.png')
drawing.set_shape_style('R1','fillColor','#ff0000')
drawing.set_shape_style('R2','fillColor','#0000ff')
drawing.set_shape_style('not existing','fillColor','#0000ff')

print(drawing.xml())