
_strList = [
            "last_opened_file",
            "MainWindow",
            "Geometry",
            "State",
          ]

# Экспортируем "короткие" алиасы имен атрибутов ( будет доступно по SGT.s_nodeType, SGT.s_x и т.д. )
for str_item in _strList:
    locals()[ "s_" + str_item ] = str_item