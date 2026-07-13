"""
map_loader.py

OSM(OpenStreetMap)을 이용하여
대구광역시 달서구의 도로망을 불러오는 모듈
"""

import random
import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt


class MapLoader:

    def __init__(self,
                 place_name="Dalseo-gu, Daegu, South Korea",
                 network_type="drive"):

        self.place_name = place_name
        self.network_type = network_type

        # 도로 그래프
        self.graph = None

        # 노드와 엣지
        self.nodes = None
        self.edges = None

        # 지도 경계
        self.north = None
        self.south = None
        self.east = None
        self.west = None

    # =====================================================
    # 지도 불러오기
    # =====================================================

    def load_map(self):
        """
        OpenStreetMap에서 달서구 도로망 다운로드
        """

        print(f"\n[{self.place_name}] 지도 불러오는 중...")

        self.graph = ox.graph_from_place(
            self.place_name,
            network_type=self.network_type,
            simplify=True
        )


        self.graph = ox.project_graph(
            self.graph
        )

        self.nodes, self.edges = ox.graph_to_gdfs(self.graph)

        self._set_boundary()

        print("지도 불러오기 완료")

        return self.graph

    # =====================================================
    # 지도 경계 저장
    # =====================================================

    def _set_boundary(self):

        self.north = self.nodes["y"].max()
        self.south = self.nodes["y"].min()

        self.east = self.nodes["x"].max()
        self.west = self.nodes["x"].min()

    # =====================================================
    # 지도 출력
    # =====================================================

    def plot_map(self):

        if self.graph is None:
            raise RuntimeError("먼저 load_map()을 실행하세요.")

        fig, ax = ox.plot_graph(
            self.graph,
            node_size=0,
            edge_linewidth=0.6,
            edge_color="gray",
            bgcolor="white",
            show=False,
            close=False
        )

        plt.show()

        return fig, ax

    # =====================================================
    # 지도 경계 반환
    # =====================================================

    def get_boundary(self):

        return {
            "north": self.north,
            "south": self.south,
            "east": self.east,
            "west": self.west
        }

    # =====================================================
    # 랜덤 좌표 생성
    # =====================================================

    def get_random_point(self):
        """
        지도 범위 내 랜덤 좌표 생성
        """

        x = random.uniform(self.west, self.east)
        y = random.uniform(self.south, self.north)

        return x, y

    # =====================================================
    # 가장 가까운 노드 찾기
    # =====================================================

    def nearest_node(self, x, y):
        """
        (x,y)에 가장 가까운 도로 노드 반환
        """

        return ox.distance.nearest_nodes(
            self.graph,
            X=x,
            Y=y
        )

    # =====================================================
    # 최단경로
    # =====================================================

    def shortest_path(self, start_node, end_node):
        """
        두 노드 사이 최단경로
        """

        return nx.shortest_path(
            self.graph,
            start_node,
            end_node,
            weight="length"
        )

    # =====================================================
    # 최단거리(m)
    # =====================================================

    def shortest_distance(self, start_node, end_node):
        """
        두 노드 사이 최단거리(m)
        """

        return nx.shortest_path_length(
            self.graph,
            start_node,
            end_node,
            weight="length"
        )

    # =====================================================
    # 노드 좌표 반환
    # =====================================================

    def get_node_coordinate(self, node):

        data = self.graph.nodes[node]

        return data["x"], data["y"]

    # =====================================================
    # 경로 좌표 반환
    # =====================================================

    def get_path_coordinates(self, path):
        """
        경로를 [(x,y), ...] 형태로 반환
        """

        coords = []

        for node in path:

            x = self.graph.nodes[node]["x"]
            y = self.graph.nodes[node]["y"]

            coords.append((x, y))

        return coords

    # =====================================================
    # 경로 그리기
    # =====================================================

    def draw_path(self, path):

        fig, ax = ox.plot_graph_route(
            self.graph,
            path,
            route_color="red",
            route_linewidth=3,
            node_size=0,
            show=False,
            close=False
        )

        plt.show()

        return fig, ax


# =========================================================
# 테스트 코드
# =========================================================

if __name__ == "__main__":

    loader = MapLoader()

    loader.load_map()

    print(loader.get_boundary())

    loader.plot_map()

    x1, y1 = loader.get_random_point()
    x2, y2 = loader.get_random_point()

    start = loader.nearest_node(x1, y1)
    end = loader.nearest_node(x2, y2)

    print("시작 노드 :", start)
    print("도착 노드 :", end)

    distance = loader.shortest_distance(start, end)

    print(f"최단거리 : {distance:.2f} m")

    path = loader.shortest_path(start, end)

    loader.draw_path(path)
