def keep_positions(length, sink_count, window):
    prefix = range(min(length, sink_count))
    tail = range(max(0, length - window), length)
    return sorted(set(prefix) | set(tail))
