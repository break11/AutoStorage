#!/usr/bin/python3.7
import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.Common.StrProps_Meta import СStrProps_Meta

class Dummy_Str_Consts(metaclass = СStrProps_Meta):
    name  = None
    Error = "[Error:]"
    Error_Message = f"{Error}ERROR!!!"

class Test_Str_Consts(unittest.TestCase):
    def test_str_consts(self):
        self.assertEqual( Dummy_Str_Consts.name,  "name" )
        self.assertEqual( Dummy_Str_Consts.Error, "[Error:]" )
        self.assertEqual( Dummy_Str_Consts.Error_Message, "[Error:]ERROR!!!" )

if __name__ == "__main__":
    unittest.main()