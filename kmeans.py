from __future__ import annotations  # Only for Python 3.7+ (useless for Python 3.10)
from typing import List, Tuple, Dict, NewType
from random import uniform
import math

Abscissa = NewType("Abscissa", float)
Ordinate = NewType("Ordinate", float)


class Point:

    def __init__(self, in_x: float, in_y: float):
        self.x: float = round(in_x, 1)
        self.y: float = round(in_y, 1)

    @staticmethod
    def random(in_x_min, in_x_max, in_y_min, in_y_max) -> Point:
        return Point(uniform(in_x_min, in_x_max), uniform(in_y_min, in_y_max))

    def distance(self, in_other: Point) -> float:
        return math.sqrt(pow(self.x - in_other.x, 2) + pow(self.y - in_other.y, 2))

    @staticmethod
    def x_min_max(in_points: List[Point]) -> Tuple[Abscissa, Abscissa]:
        x_min: float = 0
        x_max: float = 0
        for point in in_points:
            if x_min > point.x:
                x_min = point.x
            if x_max < point.x:
                x_max = point.x
        return Abscissa(x_min), Abscissa(x_max)

    @staticmethod
    def y_min_max(in_points: List[Point]) -> Tuple[Ordinate, Ordinate]:
        y_min: float = 0
        y_max: float = 0
        for point in in_points:
            if y_min > point.y:
                y_min = point.y
            if y_max < point.y:
                y_max = point.y
        return Ordinate(y_min), Ordinate(y_max)

    def __repr__(self) -> str:
        return "Point({}, {})".format(self.x, self.y)

    def __str__(self) -> str:
        return "({}, {})".format(self.x, self.y)

    def __eq__(self, in_other: Point) -> bool:
        return self.x == in_other.x and self.y == in_other.y

    def __ne__(self, in_other: Point) -> bool:
        return not self.__eq__(in_other)

    def __hash__(self) -> int:
        return hash("{},{}".format(self.x, self.y))


Barycenter = NewType("Barycenter", Point)


def kmeans(in_points: List[Point], in_k: int) -> Dict[Barycenter, List[Point]]:
    """
    Apply the "k-means" clustering technique to a set of points.
    :param in_points: the set of points.
    :param in_k: the number of partitions to find.
    :return: a set of associations between "partition barycenter" and list of points.
    """

    def _choose_barycenters(_in_points: List[Point], _in_k: int) -> List[Barycenter]:
        """
        Choose K barycenters within a set of in_points.
        :param _in_points: the set of in_points.
        :param _in_k: the number of barycenters to choose.
        :return: a list of K barycenters.
        """
        _result: List[Barycenter] = []
        selected: Dict[Abscissa, Dict[Ordinate, None]] = {}
        x_min, x_max = Point.x_min_max(_in_points)
        y_min, y_max = Point.y_min_max(_in_points)
        while True:
            x = Abscissa(round(uniform(x_min, x_max), 1))
            y = Ordinate(round(uniform(y_min, y_max), 1))
            if y in selected.get(x, {}):
                continue
            if x not in selected:
                selected[x] = {}
            selected[x][y] = None
            _result.append(Barycenter(Point(x, y)))
            if len(_result) == _in_k:
                return _result

    def _assign_barycenters(_in_points: List[Point], _in_barycenters: List[Barycenter]) -> Dict[Point, Barycenter]:
        """
        Assign one (closest) barycenter to each point.
        :param _in_points: the list of in_points.
        :param _in_barycenters: the list of barycenters.
        :return: a dictionary that associates one barycenter to one point.
        """
        distance = NewType("distance", float)
        distances: Dict[Point, Dict[Barycenter, distance]] = {}
        # For each point: calculate the distance between the point and (all) the barycenters.
        for _point in _in_points:
            distances[_point] = {}
            for _barycenter in _in_barycenters:
                distances[_point][Barycenter(_barycenter)] = distance(_point.distance(_barycenter))
        result: Dict[Point, _point_barycenter] = {}
        for _point, dist in distances.items():
            result[_point] = min(dist, key=dist.get)
        return result

    def _find_barycenter(_in_points: List[Point]) -> Barycenter:
        """
        Given a list of in_points, find the barycenter.
        :param _in_points: the list of in_points.
        :return: the barycenter.
        """
        return Barycenter(Point(sum([p.x for p in _in_points]) / len(_in_points), sum([p.y for p in _in_points]) / len(_in_points)))

    def _find_barycenters(_in_barycenter_points: Dict[Barycenter, List[Point]]) -> \
            Tuple[bool, Dict[Barycenter, List[Point]]]:
        """
        Given associations between "barycenter candidates" and lists of in_points, calculate the "real" barycenter
        and test whether the candidates are valid or not.
        :param _in_barycenter_points: associations between "barycenter candidates" and lists of in_points.
        :return: the function returns 2 values.
        - The first value tells whether all the "barycenters candidates" are valid or not.
        - The second is a set of associations between "real barycenters" and lists of in_points.
        """
        result: Dict[_point_barycenter, List[Point]] = {}
        _changed = False
        for b, pts in _in_barycenter_points.items():
            new_b = _find_barycenter(pts)
            if b != new_b:
                _changed = True
            result[Barycenter(new_b)] = pts
        return _changed, result

    barycenters: List[Barycenter] = _choose_barycenters(in_points, in_k)
    while True:
        # Assign one barycenter to each point. The assigned barycenter is the closest one to the point.
        _point_barycenter: Dict[Point, _point_barycenter] = _assign_barycenters(in_points, barycenters)
        # Group the in_points that have the same barycenter.
        _barycenter_points: Dict[Barycenter, List[Point]] = {n: [k for k in _point_barycenter.keys()
                                                                 if _point_barycenter[k] == n]
                                                             for n in set(_point_barycenter.values())}
        print("[1] " + "-" * 30)
        for _barycenter, _points in _barycenter_points.items():
            print('[{}]:{}'.format(", ".join([str(p) for p in _points]), _barycenter), flush=True)

        # Calculate the (real) barycenters of the previously formed groups.
        _barycenter_points: Dict[Barycenter, List[Point]]
        changed, _barycenter_points = _find_barycenters(_barycenter_points)

        print("[2] " + "-" * 30)
        for _barycenter, _points in _barycenter_points.items():
            print('[{}]:{}'.format(", ".join([str(p) for p in _points]), _barycenter), flush=True)
        print('Changed: {}'.format('yes' if changed else 'no'))
        if not changed:
            break
        barycenters = list(_barycenter_points.keys())
    return _barycenter_points


POINTS_COUNT: int = 10
K: int = 4
list_of_points = [Point.random(0, 20, 0, 20) for _ in range(POINTS_COUNT)]
barycenter_points = kmeans(list_of_points, K)

print("We found the partitions!")
for barycenter, points in barycenter_points.items():
    print('[{}]:{}'.format(", ".join([str(p) for p in points]), barycenter))
