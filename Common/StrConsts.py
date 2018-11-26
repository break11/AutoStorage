
_strList = [
            "last_opened_file",
            "storage_graph_file",
            "main_window",
            "geometry",
            "state",
            "scene",
            "grid_size",
            "draw_grid",
            "draw_info_rails",
            "draw_main_rail",
          ]

# Экспортируем "короткие" алиасы имен атрибутов ( будет доступно по SGT.s_nodeType, SGT.s_x и т.д. )
for str_item in _strList:
    locals()[ "s_" + str_item ] = str_item
