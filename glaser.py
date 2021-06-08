# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 12:17:12 2021

@author: Anssi Laukkarinen, 2021
"""

import xml.etree.ElementTree as ET

tree = ET.parse('material_db.xml')
root_materials_db = tree.getroot()


# Print whole materials database
# for material in root_materials_db:
#     print(material.get('name'))
#     for children in material:
#         print(children.tag, children.text)
#     print('\n')
        

# Print only listed materials
used_materials = ['Betoni_1pros_kuiva', 'Betoni_1pros_märkä']

material_data = {}

for used_material in used_materials:
    
    for material in root_materials_db:
        
        if material.get('name') == used_material:
            name = used_material
            lam = material.find('lambda').text
            mu = material.find('mu').text
            dummy = {'lambda': float(lam), 'mu': float(mu)}
            material_data[used_material] = dummy



