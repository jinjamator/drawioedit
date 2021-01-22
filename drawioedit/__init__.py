
from crc32c import crc32c
import sys
from N2G import drawio_diagram
import requests
import logging

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
        

    def load_from_file(self, file_path, file_type=None):
        self._source_file_path=file_path
        if not file_type:
            if file_path.lower().endswith('png'):
                file_type='png'
        if file_type == 'png':
            self._src_xml=self.extract_xml_from_png(file_path)
            self.load_from_string(self._src_xml)

        else:
            raise ValueError(f'unsupported filetype {file_type}')
    
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
        

    def load_from_string(self, data):
        self._diagram = drawio_diagram()
        return self._diagram.from_xml(data)
    
    def find_object_by_attribute(self,attribute_name, attribute_value):
        return self._diagram.current_root.find(f"./object[@{attribute_name}='{attribute_value}']")
        
    def set_shape_style(self, search_value , key, value, search_attribute = 'label'):
        node = self.find_object_by_attribute(search_attribute, search_value)
        if not node:
            self._log.error(f'object "{search_attribute}"="{search_value}" not found -> ignoring')
            return False
        cell=node.find('./mxCell')        
        src_style=cell.attrib.get('style').split(';')
        styles={}
        for style in src_style:
            if style:
                k,v = style.split('=')
                styles[k]=v
        if value == None:
            del styles[key]
        else:
            styles[key]=value
        dst_style = []
        for k,v in styles.items():
            dst_style.append(f'{k}={v}')
        dst_style.append('')
        str_style = ';'.join(dst_style)
        self._diagram.update_node(node.attrib.get('id'), style=str_style)
    
    def xml(self):
        return self._diagram.dump_xml()

    def save(self, destination_file):
        pass
