from typing import List
import xml.etree.ElementTree as ET

"""
TODO:
1. Make parsing better:
    i. Splitting by space is error prone (scale extraction)
"""

class SvgPathExtractor:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()

        self.svg_g = self.get_g_elements()
        self.svg_paths = self.get_paths_from_g(self.svg_g)
    
    def get_g_elements(self):
        return self.get_g_elements_util(self.root)

    def get_g_elements_util(self, root):
        root_tag = "".join(root.tag.split("{http://www.w3.org/2000/svg}"))
        if "g" == root_tag:
            return [root]
        
        g_elements = []
        for child in root:
            g_elements += self.get_g_elements_util(child)
        return g_elements

    def get_paths_from_g(self, elements: List) -> List:
        svg_paths = []
        for g in elements:
            transforms = g.get("transform").split(" ")
            scale = {"x": 1.0, "y": 1.0}
            for transform in transforms:
                if len(transform) > 5 and transform[:5] == "scale":
                    scale_xy = transform[7:-1].split(",")
                    scale["x"] = float(scale_xy[0])
                    scale["y"] = float(scale_xy[1])

            paths = self.get_paths_util(g)
            svg_paths.append({"scale": scale, "paths": paths})
        return svg_paths
            
    def get_paths(self) -> list:
        return self.get_paths_util(self.root)

    def get_paths_util(self, root) -> List:
        root_tag = "".join(root.tag.split("{http://www.w3.org/2000/svg}"))
        if "path" == root_tag:
            return [root.get("d")]

        paths = []
        for child in root:
            paths += self.get_paths_util(child)
        return paths
    
test = SvgPathExtractor("dickbutt.svg")