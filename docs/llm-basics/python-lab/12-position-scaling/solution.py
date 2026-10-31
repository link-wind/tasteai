def scale_positions(positions, scale):
    if scale <= 0:
        raise ValueError("scale 必须大于0")
    return [p / scale for p in positions]
