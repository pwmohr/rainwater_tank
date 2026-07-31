import math

d = 0.6

# Because of the periodicity of the sin/asin functions, we will calculate what
# fraction of a representative 1 m^3 tank would be full at the current depth,
# then map that to the actual volume of the real tank. 
tnkDepth = 2.25 # m
tankLength = 6.4 # m
tankVolume = tankLength * math.pi * (tankDepth/2.0)**2
fracDepth = d / tankDepth

# Calculate fractional volume for a 1 m^3 tank at the current fractional Depth
length = 1 # tank length, meters
radius = 0.5 # tank radius, meters

# Note: volume calculation comes from Natalie's exact calculus solution for a cylinder laying
# on its side. It does not yet include the semi-spherical end-cap volumes, so is an underestimate
# of the total water volume.
volume = abs(length*radius**2*(math.asin((radius-fracDepth)/radius)-math.pi/2+0.5*math.sin(2*math.asin((radius-fracDepth)/radius))));
fracVolume = volume / (math.pi/4.0)

waterVolume = fracVolume * tankVolume # m^3

# Convert volume into gallons
# 1 m^3 -> 296.91 gallons
waterVolumeGal = waterVolume * 296.91

print('For depth = ' + str(d) + 'm, Volume = ' + str(waterVolumeGal) + ' gallons')