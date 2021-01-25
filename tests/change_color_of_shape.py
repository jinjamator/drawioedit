import sys
sys.path.insert(0, "../")
from drawioedit import DrawIOEdit
import os
red='#ff0000'
base_path=os.path.dirname(os.path.realpath(__file__))
drawing=DrawIOEdit(file_path=f'{base_path}/input.drawio.svg')
drawing.set_shape_color('DC1-SW1',red)
drawing.set_shape_color('bbnew-1',red)
drawing.set_shape_color('iperf-1',red)
drawing.set_shape_color('iperf-3',red)



for link in drawing.find_link_between_nodes('DC1-SW1','bbnew-1'):
    link.attrib['style']=drawing._edit_style(link.attrib['style'],'strokeColor','#ff0000')

for link in drawing.find_link_between_nodes('Backbone-1','BB-new'):
    link.attrib['style']=drawing._edit_style(link.attrib['style'],'strokeColor','#ff0000')



print(drawing.xml())