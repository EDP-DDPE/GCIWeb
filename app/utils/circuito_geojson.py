import json, os
import threading
import numpy as np
import shapely
from shapely.geometry import Point, shape
from pyproj import Transformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEOJSON_PATH = os.path.join(BASE_DIR, "..", "..", "data", "circuitos.geojson")

# Projeção métrica para cálculo de distância. Em vez de fixar uma zona UTM
# (31983 = zona 23S, boa p/ SP mas com ~0.3% de erro no ES por extrapolação),
# usamos um Transverse Mercator com meridiano central -43° (entre SP e ES).
# Assim ambas as regionais ficam a <3° do CM -> distorção <= ~0.13% nas duas.
# always_xy=True -> entrada/saída na ordem (lon/x, lat/y)
_CRS_METRICO = (
    "+proj=tmerc +lat_0=0 +lon_0=-43 +k=0.9996 "
    "+x_0=500000 +y_0=10000000 +ellps=GRS80 +units=m +no_defs"
)
_transformer = Transformer.from_crs("EPSG:4326", _CRS_METRICO, always_xy=True)
_to_utm = _transformer.transform


class CircuitoIndex:
    def __init__(self, path):
        self.mtime = os.path.getmtime(path)
        print("Carregando circuitos (GeoJSON)...")
        with open(path, encoding="utf-8") as f:
            fc = json.load(f)

        self.features = fc["features"]                       # geometria lat/lon original p/ o front
        self.props = [feat["properties"] for feat in self.features]

        # Reprojeção VETORIZADA: converte todos os vértices de todos os circuitos
        # de uma só vez (1 chamada ao pyproj), em vez de vértice a vértice.
        geoms_ll = np.array([shape(feat["geometry"]) for feat in self.features], dtype=object)
        coords = shapely.get_coordinates(geoms_ll)           # (total_vertices, 2) em lon/lat
        tx, ty = _to_utm(coords[:, 0], coords[:, 1])         # projeta tudo de uma vez
        self.geoms_arr = shapely.set_coordinates(geoms_ll, np.column_stack([tx, ty]))
        print(f"Circuitos carregados: {len(self.features)}")

    def mais_proximos(self, lat, lon, k=3, regional=None):
        x, y = _to_utm(lon, lat)
        ponto = Point(x, y)
        dists = shapely.distance(ponto, self.geoms_arr)      # distância (m) p/ todos os circuitos
        cand = []
        for i in np.argsort(dists):                          # do mais próximo ao mais distante
            i = int(i)
            if regional is not None and self.props[i]["regional"] != regional:
                continue
            cand.append((i, float(dists[i])))
            if len(cand) >= k:
                break
        return cand


_index = None
_lock = threading.Lock()


def get_index(force=False):
    """Índice global, carregado UMA única vez por processo e compartilhado por
    todas as threads/workers do Flask. Use force=True (ou recarregue o app) quando
    o GeoJSON diário for atualizado."""
    global _index
    if _index is None or force:
        with _lock:                                          # 2 requests simultâneos não carregam 2x
            if _index is None or force:
                _index = CircuitoIndex(GEOJSON_PATH)
    return _index
