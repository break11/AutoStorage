
sWarning = "[Warning]:"
sError   = "[Error]:"
sAssert  = "[Assert]:"

_strList = [
            "last_opened_file",
            "storage_graph_file",
            "main_window",
            "geometry",
            "state",
            "grid_size",
            "draw_grid",
            "draw_info_rails",
            "draw_main_rail",
          ]

s_storage_graph_file__default = "GraphML/test.graphml"

# Экспортируем "короткие" алиасы строковых констант
for str_item in _strList:
    locals()[ "s_" + str_item ] = str_item
