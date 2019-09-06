
sWarning = "[Warning]:"
sError   = "[Error]:"
sAssert  = "[Assert]:"

_strList = [
            "last_opened_file",
            "storage_graph_file",
            "main_window",
            "geometry",
            "state",
            "propRef"
          ]
          
# Экспортируем "короткие" алиасы строковых констант
for str_item in _strList:
    locals()[ "s_" + str_item ] = str_item

s_storage_graph_file__default = "GraphML/test.graphml"
s_mainwindow_ui = "/mainwindow.ui"
