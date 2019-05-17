import os
import unittest

tests = []

for root, dirs, files in os.walk("./UnitTests"):
    for file in files:
        if file.startswith("ut_"):
            l = file.split( "." )
            if l[ -1 ] == "py":
                sFName = os.path.join(root, file)
                sFName = sFName.replace( "./UnitTests/", "" )
                sFName = sFName.replace( ".py", "" )
                sFName = sFName.replace( "/", "." )
                tests.append( sFName )
                # print( l[0], sFName )

print( "Finded tests:", tests )

runner = unittest.TextTestRunner(verbosity=2)
testLoad = unittest.TestLoader()

rd = {}
bResult = True
for test in tests:
    suite = testLoad.loadTestsFromName( test )
    b = runner.run( suite ).wasSuccessful()
    rd[ test ] = b
    bResult = bResult and b
    # if not runner.run( suite ).wasSuccessful():
    #     break

if not bResult:
    print( "!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!" )
else:
    print( "**************** OK **********************" )

rString = { True : "OK", False : "FAILED !!!!" }

print( "*****************************************" )
for k,v in rd.items():
    while len( k ) < 50:
        k += " "

    print( k, "=\t", rString[ v ] )
print( "*****************************************" )
print( "*****************************************" )
