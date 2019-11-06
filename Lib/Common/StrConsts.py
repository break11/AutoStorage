
from Lib.Common.StrProps_Meta import СStrProps_Meta

class SC( metaclass = СStrProps_Meta ):
    last_opened_file    = None
    storage_graph_file  = None
    main_window         = None
    geometry            = None
    state               = None
    propRef             = None
    name                = None
    UID                 = None
    sWarning            = "[Warning]:"
    sError              = "[Error]:"
    sAssert             = "[Assert]:"

    storage_graph_file__default = "GraphML/test.graphml"
    mainwindow_ui               = "/mainwindow.ui"
    No_Graph_loaded             = f"{sWarning} No Graph loaded."
