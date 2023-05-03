# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 16:16:21 2022

@author: matth
"""

from PlotGraph import PlotGraph
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from mayavi import mlab
from mpl_toolkits import mplot3d
from matplotlib.tri import Triangulation
from matplotlib.ticker import LinearLocator

#matplotlib inline
import numpy as np
import matplotlib.pyplot as plt


def f(x, y):
    return np.sin(np.sqrt(x ** 2 + y ** 2))

def get_plot_data(text):

    dataPoint = 0
    fileData = []

    for dataString in text:
        dataPointString = ''
        dataTuple = []
        for tempChar in dataString:
            if tempChar == ',' or tempChar == '\n':
                dataPoint = float(dataPointString)
                dataTuple.append(dataPoint)
                dataPointString = ''
            else:
                dataPointString += tempChar
        fileData.append((dataTuple[0],dataTuple[1],dataTuple[2],dataTuple[3]))
    return fileData;


# x = np.linspace(-6, 6, 30)
# y = np.linspace(-6, 6, 30)

# X, Y = np.meshgrid(x, y)
# Z = f(X, Y)

# fig = plt.figure()
# ax = plt.axes(projection='3d')
# ax.contour3D(X, Y, Z, 50, cmap='binary')
# ax.set_xlabel('x')
# ax.set_ylabel('y')
# ax.set_zlabel('z');



# r = np.linspace(0, 6, 20)
# theta = np.linspace(-0.9 * np.pi, 0.8 * np.pi, 40)
# r, theta = np.meshgrid(r, theta)

# X = r * np.sin(theta)
# Y = r * np.cos(theta)
# Z = f(X, Y)

# ax = plt.axes(projection='3d')
# ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
#                 cmap='viridis', edgecolor='none');


# theta = 2 * np.pi * np.random.random(1000)
# r = 6 * np.random.random(1000)
# x = np.ravel(r * np.sin(theta))
# y = np.ravel(r * np.cos(theta))
# z = f(x, y)

# ax = plt.axes(projection='3d')
# ax.scatter(x, y, z, c=z, cmap='viridis', linewidth=0.5);
# ax = plt.axes(projection='3d')
# ax.plot_trisurf(x, y, z,
#                 cmap='viridis', edgecolor='none');



fileName = input("Enter the name of the data you want to plot\n")
fr = open(fileName)
text = fr.readlines()
fr.close()
text.remove(text[0])
text.remove(text[0])
fileData = get_plot_data(text);


plot_graph = PlotGraph(fileData, fileName)
plot_graph.show()

# print(fileData)

test, test1, test2, test3 = zip(*fileData)


# print(test)
# print(test3)


# print(test1)

r = test3
theta = test

# print(theta)
theta = list(theta)
for i in range(len(theta)):
    theta[i] = theta[i]*np.pi/180

phi = test1
phi = list(phi)

for i in range(len(phi)):
    phi[i] = phi[i]*np.pi/180

# print(r)
r = list(r)
rnorm = max(r)
print(rnorm)
for i in range(len(r)):
    r[i]=r[i]/rnorm

r = r[::40]
theta = theta[::40]
phi = phi[::40]


# print(r)
# print(phi)

# print(theta)
y = np.ravel(r * np.sin(theta)*np.cos(phi))
x = np.ravel(r * np.cos(theta)*np.cos(phi))
z = np.ravel(r * np.sin(phi))
 


# y = y[::10]
# x = x[::10]
# z = z[::10]
# x = np.ravel(r * np.sin(theta)*np.cos(phi))
# y = np.ravel(r * np.sin(theta)*np.sin(phi))
# z = np.ravel(r * np.cos(phi))

# print(z)



test4 = np.zeros(len(r))
test4 = list(test4)
for i in range(len(test4)):
    if r[i] > 0.9 :
        test4[i] = 'r'
    elif r[i] > 0.8:
        test4[i] = 'orange'
    elif r[i] > 0.7:
        test4[i] = 'y'
    elif r[i] > 0.6:
        test4[i] = 'lime'
    elif r[i] > 0.5:
        test4[i] = 'g'
    elif r[i] > 0.3:
        test4[i] = 'c'
    else:
        test4[i] = 'b'




# cb1 = mpl.colorbar.ColorbarBase(ax1, cmap = 'hsv', norm=norm,orientation='horizontal')

# ax = plt.axes(projection='3d')
# ax.scatter(x, y, z, c=test4);


# datasets = {"x": [1,0,0], "y":[0,1,0], "z":[0,0,1]}

# fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
# for key,p in datasets.items():
#     ax.plot([0,p[0]], [0,p[1]], [0,p[2]], label=key)
#     ax.scatter(x, y, z, c=test4);
# ax.legend()

# plt.show()


# ax = plt.axes(projection='3d')
# ax.plot_trisurf(x, y, z,
#                 color='r', edgecolor='none');


# tri = Triangulation(np.ravel(phi), np.ravel(theta))
  
# ax = plt.axes(projection ='3d')
# ax.plot_trisurf(x, y, z, triangles = tri.triangles,
#                 cmap ='magma', linewidths = 0.5);



tri = Triangulation(np.ravel(phi), np.ravel(theta))
fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
ax.plot([0,1],[0,0],[0,0], label = 'x', color = 'b')
ax.plot([0,0],[0,1],[0,0], label = 'y', color = 'g')
ax.plot([0,0],[0,0],[0,1], label = 'z', color = 'r' )
# ax.scatter(x, y, z, c=test4, alpha=1);
ax.plot_trisurf(x, y, z, triangles = tri.triangles,
                    cmap=plt.cm.CMRmap, linewidths = 0.5, antialiased=True);
# ax.scatter(x, y, z, c=test4, alpha=1);
# ax.plot([0,0[0]], [0,0[1]], [0,0[2]], label='x', color = 'r')
ax.grid(False)    
ax.legend()
ax.set_xticks([])
ax.set_yticks([])
ax.set_zticks([])
plt.axis('off')
plt.show()



# d = np.sqrt(x**2+y**2+z**2)
# d = d/d.max()




# fig = plt.figure()
# ax = fig.gca(projection='3d')
# d = np.sqrt(x**2+y**2+z**2)
# d = d/d.max()
# # surf = ax.plot_surface(x, y, z, facecolors=plt.cm.viridis(d), linewidth=0)
# surf = ax.plot_trisurf(x, y, z, linewidth=0, antialiased=False)

# tri = Triangulation(np.ravel(phi), np.ravel(theta))
  
# ax = plt.axes(projection ='3d')
# ax.plot_trisurf(x, y, z, triangles = tri.triangles,
#                 color=(1,0,0,0), linewidths = 0.5);



# ax = plt.axes(projection='3d')
# ax.scatter3D(x, y, z, c=z, cmap='Greens');
# ax.scatter(x, y, z, c=z, cmap='viridis', linewidth=0.5);
# ax.plot3D(x, y, z, 'gray')

# ax = plt.axes(projection='3d')
# ax.plot_trisurf(x, y, z,
#                 cmap='viridis', edgecolor='none');


# ax = plt.axes(projection='3d')
# ax.plot_trisurf(x, y, z,
#                 cmap='viridis', edgecolor='none');

ax.view_init(45, 45)



# open antenna scan log file and add data header
filename_prefix = "BlenderTest"
filename = filename_prefix + ".txt"
datafile_fp = open(filename, 'w')
for i in range(len(x)):
    datafile_fp.write(str(x[i]) + ',' + str(y[i]) + ',' + str(z[i]) + '\n')

datafile_fp.close();