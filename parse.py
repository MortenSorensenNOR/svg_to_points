import svg.path
import numpy as np

from typing import List
from svg_parse.read import SvgPathExtractor
from scipy.interpolate import interp1d

class SvgToPoints:
    def __init__(self, file_path: str, samples: int) -> None:
        # Read
        self.path_extractor = SvgPathExtractor(file_path)
        self.paths = self.path_extractor.get_paths()
        
        # Parse
        self.samples = samples
        assert self.samples > 1

        self.path_data = []
        for path in self.paths:
            self.path_data.append(svg.path.parse_path(path))

        self.point_data = []
        for path in self.path_data:
            points = self.get_points_from_path(path)
            self.point_data.append(points)

        self.point_data_xy = []
        for points in self.point_data:
            xy_points = []
            for point in points:
                xy_points.append(self.svg_point_to_coordinate(point))
            self.point_data_xy.append(xy_points)

        self.concatinated_point_data_xy = []
        for points in self.point_data_xy:
            self.concatinated_point_data_xy += points

        # Parse 2
        self.svg_paths = self.path_extractor.svg_paths
        self.svg_points = []
        for g in self.svg_paths:
            scale = g["scale"]
            paths = g["paths"]

            path_data = []
            for path in paths:
                path_data.append(svg.path.parse_path(path))
            
            point_data = []
            for path in path_data:
                points = self.get_points_from_path(path)
                point_data.append(points)
            
            point_data_xy = []
            for points in point_data:
                xy_points = []
                for point in points:
                    xy_point = self.svg_point_to_coordinate(point)
                    xy_point[0] *= scale["x"]
                    xy_point[1] *= scale["y"]
                    xy_points.append(xy_point)
                point_data_xy.append(xy_points)
            
            for points in point_data_xy:
                self.svg_points += points

        self.svg_points_normalized = self.normalize_points(self.svg_points)

    """ ==================================================== """
    def normalize_points(self, points):
        x_min, x_max = 1 << 32, -(1 << 32)
        y_min, y_max = 1 << 32, -(1 << 32)
        for [x, y] in points:
            if x < x_min:
                x_min = x
            if x > x_max:
                x_max = x
            if y < y_min:
                y_min = y
            if y > y_max:
                y_max = y

        map_x = interp1d([x_min, x_max], [-1.0, 1.0])
        map_y = interp1d([y_min, y_max], [-1.0, 1.0])

        new_points = []
        for [x, y] in points:
            x_new = map_x(x)
            y_new = map_y(y)
            new_points.append([x_new, y_new])
        return new_points

    def svg_point_to_coordinate(self, point: complex) -> List:
        return [point.real, point.imag]
    
    def get_points_from_path(self, path):
        if self.path_data == []:
            print("No path data has been initilized")
            return

        points = []
        for segment in path:
            if isinstance(segment, svg.path.Line):
                points += self.sample_line(segment)
            elif isinstance(segment, svg.path.Arc):
                points += self.sample_arc(segment, self.samples)
            elif isinstance(segment, svg.path.CubicBezier):
                points += self.sample_cubic_bezier(segment, self.samples)
            elif isinstance(segment, svg.path.QuadraticBezier):
                points += self.sample_quadratic_bezier(segment, self.samples)

        return points
    
    def sample_line(self, line: svg.path.Line):
        return [line.start, line.end]

    def sample_arc(self, curve: svg.path.Arc, samples: int) -> List:
        points = []
        for i in range(samples):
            points.append(curve.point(i/(samples-1)))
        return points

    def sample_cubic_bezier(self, curve: svg.path.CubicBezier, samples: int) -> List:
        points = []
        for i in range(samples):
            points.append(curve.point(i/(samples-1)))
        return points

    def sample_quadratic_bezier(self, curve: svg.path.QuadraticBezier, samples: int) -> List:
        points = []
        for i in range(samples):
            points.append(curve.point(i/(samples-1)))
        return points