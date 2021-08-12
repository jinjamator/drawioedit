
from crc32c import crc32c
import sys
from .N2G_DrawIO import drawio_diagram
import requests
import logging
import xml.etree.ElementTree as ET
import zlib
import base64
import html
import subprocess
import tempfile
import os

class InvalidCRCError(BaseException):
    pass

class EOF(BaseException):
    pass

class DrawIOEdit(object):
    def __init__(self, file_path=None, xml=None):
        self._diagram = None
        self._source_file_path=None
        self._log = logging.getLogger(__file__)
        if file_path:
            self.load_from_file(file_path)
        self._drawing = None
        self._draw_io_path='/usr/bin/drawio'
        self._xvfb_run_path='/usr/bin/xvfb-run'

        

    def load_from_file(self, file_path, file_type=None):
        self._source_file_path=file_path
        if not file_type:
            if file_path.lower().endswith('png'):
                file_type='png'
            elif file_path.lower().endswith('svg'):
                file_type='svg'
        if file_type == 'png':
            self.extract_xml_from_png(file_path)
            self.load_from_string(self._src_xml)
        if file_type == 'svg':
            self.extract_xml_from_svg(file_path)
            self.load_from_string(self._src_xml)

        else:
            raise ValueError(f'unsupported filetype {file_type}')
        # print(self._src_xml)
    
    def _read_png_section(self, f):
        section_length = int.from_bytes(f.read(4), byteorder='big',signed=False)
        section_type = f.read(4)
        if section_type == b'':
            raise EOF()
        section_content = f.read(section_length)
        section_crc=f.read(4)
        if crc32c(section_content) != section_crc:
            # print(int(section_crc.hex(),16))
            # print(crc32c(section_content))
            # raise InvalidCRCError(f"{self._source_file_path} section {section_type.decode('latin-1')} has invalid CRC -> data is probably corrupted")
            pass
        
        return (section_type.decode('latin-1'), section_content)

    def extract_xml_from_png(self, file_path):
        self._src_xml = None
        with open(file_path, "rb") as f:
            header = f.read(8)
            if header !=  b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a": # PNG header
                raise TypeError(f"{file_path} is not a valid PNG file")
            
            try:
                while True:
                    section_type, section_content = self._read_png_section(f)
                    if section_type == 'tEXt':                        
                        k,v = section_content.decode('latin-1').split(b'\x00'.decode('latin-1'))
                        if k == 'mxfile':
                            self._src_xml = requests.utils.unquote(v)
            except EOF:
                if not self._src_xml:
                    raise ValueError(f'Cannot find drawio drawing embedded in {self._source_file_path}')
        return self._src_xml
    
    def extract_xml_from_svg(self,file_path):
        self._src_xml = None
        with open(file_path, "r") as f:
            svg_xml=f.read()
            svg_root=ET.fromstring(svg_xml)
            orig_xml=svg_root.attrib.get('content')
            dig_root=ET.fromstring(orig_xml)
            for doc in dig_root.findall('./diagram'):
                xmlb=zlib.decompress(base64.b64decode( doc.text), -15)
                doc.text=""
                dxml=ET.fromstring(requests.utils.unquote(xmlb.decode('latin-1')))
                doc.insert(0,dxml)
            self._src_xml = ET.tostring(dig_root).decode('utf-8')
        return self._src_xml

    def load_from_string(self, data):
        self._diagram = drawio_diagram()
        return self._diagram.from_xml(data)
    
    def find_object_by_attribute(self,attribute_name, attribute_value):
        return self._diagram.current_root.find(f"./object[@{attribute_name}='{attribute_value}']")
    
    def find_cell_by_attribute(self,attribute_name, attribute_value):
        return self._diagram.current_root.find(f"./mxCell[@{attribute_name}='{attribute_value}']")

    def find_any_by_label_or_value(self, search_value):
        node = self.find_object_by_attribute('label', search_value)
        if not node:
            search_attribute='value'
            node=self.find_cell_by_attribute('value', search_value)
        if not node:
            self._log.error(f'cannot find anything with the label or value of: {search_value}')
        return node
 

    def _parse_style(self,style):
        if not style:
            return {}
        src_style=style.split(';')
        styles={}
        for style in src_style:
            if '=' in style:
                k,v = style.split('=')
                styles[k]=v
            elif not style or style == 'image':
                pass
        return styles

    def _edit_style(self,style,key,value):
        styles = self._parse_style(style)
        if value == None:
            del styles[key]
        else:
            styles[key]=value
        dst_style = []
        for k,v in styles.items():
            if k == 'image':
                dst_style.append(k)
            
            dst_style.append(f'{k}={v}')
        dst_style.append('')
        str_style = ';'.join(dst_style)
        return str_style

    def set_shape_color(self,search_value,color_code,search_attribute='label'):
        node = self.find_object_by_attribute(search_attribute, search_value)
        if not node:
            search_attribute='value'
            node=self.find_cell_by_attribute(search_attribute, search_value)
        if not node:
            self._log.error(f'cannot find shape {search_attribute} {search_value}')
            return False
        
        

        if node.tag.lower() == 'object': # edit object
            cell = node.find('mxCell')
            src_style = cell.attrib.get('style')
            if 'image' in self._parse_style(src_style): # edit image mxcell in object
                if color_code:
                    dst_style=self._edit_style(src_style,'imageBackground',color_code)
                    dst_style=self._edit_style(dst_style,'fillOpacity','50')
                else:
                    dst_style=self._edit_style(src_style,'imageBackground',color_code)
                    dst_style=self._edit_style(dst_style,'fillOpacity','100')

                cell.attrib['style']=dst_style
            else:
                if not color_code:
                    color_code="#999999"
                dst_style=self._edit_style(src_style,'fillColor',color_code)

        elif node.tag.lower() == 'mxcell': # mxcell
            src_style = node.attrib.get('style')
            if 'image' in self._parse_style(src_style): # edit image mxcell
                if color_code:
                    dst_style=self._edit_style(src_style,'imageBackground',color_code)
                    dst_style=self._edit_style(dst_style,'fillOpacity','50')
                else:
                    dst_style=self._edit_style(src_style,'imageBackground',color_code)
                    dst_style=self._edit_style(dst_style,'fillOpacity','100')
                node.attrib['style']=dst_style
            else:
                if not color_code:
                    color_code="#999999"
                dst_style=self._edit_style(src_style,'fillColor',color_code)                
        else:
            self._log.error(f'unknown node type {node.tag}')
            return False

        self._diagram.update_node(node.attrib.get('id'), style=dst_style)       
        return True

    def set_shape_style(self, search_value , key, value, search_attribute = 'label'):
        node = self.find_object_by_attribute(search_attribute, search_value)
        if not node:
            self._log.error(f'object "{search_attribute}"="{search_value}" not found -> ignoring')
            search_attribute='value'
            cell = self.find_cell_by_attribute(search_attribute, search_value)
            node=cell
            if not node:
                self._log.error(f'mxCell "{search_attribute}"="{search_value}" not found -> ignoring')
                return False
        else:
            cell=node.find('./mxCell') 

        str_style=self._edit_style(cell.attrib.get('style'))
        self._diagram.update_node(node.attrib.get('id'), style=str_style)
        return True
    
    def xml(self):
        return self._diagram.dump_xml()

    def save(self, destination_file):
        if destination_file.endswith('.drawio'):
            with open(destination_file,'w') as tmp_fh:
                tmp_fh.write(self.xml())
            
        elif destination_file.endswith('.png') or destination_file.endswith('.svg') or destination_file.endswith('.jpg'):
            if not os.path.exists(self._xvfb_run_path):
                raise Exception(f'xvfb-run not found in configured path ({self._xvfb_run_path}), perhaps you should run "sudo apt install xvfb"')
            if not os.path.exists(self._draw_io_path):
                raise Exception(f'drawio desktop not found in configured path ({self._draw_io_path}), perhaps you should run "wget \'https://github.com/jgraph/drawio-desktop/releases/download/v14.1.8/draw.io-amd64-14.1.8.deb\' && sudo dpkg -i draw.io-amd64-14.1.8.deb && sudo apt-get install -f"')
            tmp_fd,tmp_path=tempfile.mkstemp(suffix='.drawio')
            with os.fdopen(tmp_fd,'w') as tmp_fh:
                tmp_fh.write(self.xml())
            result=subprocess.check_output([self._xvfb_run_path,"-a",self._draw_io_path,"-x","-e","-o",destination_file,tmp_path],universal_newlines=True)
            self._log.debug(result)
            os.unlink(tmp_path)
        else:
            raise ValueError(f'{destination_file} is missing supported file extension .drawio .drawio.svg .drawio.png')
        
        
    
    def find_link_between_nodes(self,node_a, node_b):
        links = []
        try:
            node_a_id = self.find_any_by_label_or_value(node_a).attrib.get('id')
        except AttributeError:
            self._log.error('cannot find node_a id -> no link found')
            return links
        try:
            node_b_id = self.find_any_by_label_or_value(node_b).attrib.get('id')
        except AttributeError:
            self._log.error('cannot find node_b id -> no link found')
            return links
        for node in self._diagram.current_root.findall(f"./*[@source='{node_a_id}']"):
            if node.attrib.get('target') == node_b_id:
                links.append(node)
        for node in self._diagram.current_root.findall(f"./*[@source='{node_b_id}']"):
            if node.attrib.get('target') == node_a_id:
                links.append(node)

        return links
        
    
        

