import re


s = "Lorem ipsum, dolor: sit; amet  consectetur| adipiscing\n elit"
reg = ";|,|:| "

print( re.split(reg, s) )