# getGrid.py
import math
import logging

RE = 6371.00877  # Earth's radius (km)
GRID = 5.0  # Grid spacing (km)
SLAT1 = 30.0  # Projection latitude 1 (degree)
SLAT2 = 60.0  # Projection latitude 2 (degree)
OLON = 126.0  # Reference point longitude (degree)
OLAT = 38.0  # Reference point latitude (degree)
XO = 43  # Reference point X coordinate (GRID)
YO = 136  # Reference point Y coordinate (GRID)

def dfs_xy_conv(code, v1, v2):
    DEGRAD = math.pi / 180.0
    RADDEG = 180.0 / math.pi

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    rs = {}

    if code == "toXY":
        rs['lat'] = v1
        rs['lng'] = v2
        ra = math.tan(math.pi * 0.25 + (v1) * DEGRAD * 0.5)
        ra = re * sf / math.pow(ra, sn)
        theta = v2 * DEGRAD - olon
        if theta > math.pi:
            theta -= 2.0 * math.pi
        if theta < -math.pi:
            theta += 2.0 * math.pi
        theta *= sn
        rs['x'] = math.floor(ra * math.sin(theta) + XO + 0.5)
        rs['y'] = math.floor(ro - ra * math.cos(theta) + YO + 0.5)

        logging.info(f"Converted lat {v1}, lng {v2} to grid coordinates x {rs['x']}, y {rs['y']}")
        return rs['x'], rs['y']

    return None
