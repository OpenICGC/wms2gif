from __future__ import print_function
import imageio
import json
import numpy as np
import socket
import urllib2
import os.path
import argparse
import random
import string

import config

def createSquareBBox(bbox):
	bBoxData = bbox.split(",")
	minLon = float(bBoxData[0])
	minLat = float(bBoxData[1])
	maxLon = float(bBoxData[2])
	maxLat = float(bBoxData[3])
	centerLon = (minLon + maxLon) / 2.0
	centerLat = (minLat + maxLat) / 2.0

	difLon = maxLon - minLon
	difLat = maxLat - minLat

	if(difLon < difLat):
		offset = difLat / 2.0
		minLon = centerLon - offset
		maxLon = centerLon + offset
	elif(difLon > difLat):
		offset = difLon / 2.0
		minLat = centerLat - offset
		maxLat = centerLat + offset
	return "{},{},{},{}".format(minLon, minLat, maxLon, maxLat)

def buildWMSURL(urlBase, layerNames, height, width, srs, bbox):
	urlService = "&SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&FORMAT=image%2Fpng&TRANSPARENT=true"
	urlFixed = urlBase + urlService
	urlVariable = "&LAYERS={}&STYLES=&HEIGHT={}&WIDTH={}&SRS={}&BBOX={}"
	url = urlFixed + urlVariable
	url = url.format(layerNames, height, width, srs, bbox)

	return url

def createGIF(name, width, height, srs, inBbox, inDuration):

	images = []
	index = 0
	bbox = createSquareBBox(inBbox)
	for layerDef in config.layerDefinitions:
		for layer in config.layerDefinitions[layerDef]:
			url = buildWMSURL(layerDef, layer["name"], width, height, srs, bbox)
			print(layer["name"] + "(" + url + ")", end='')
			try:
				image = imageio.imread(url, format="PNG", pilmode="RGBA")
			except (socket.error, urllib2.URLError):
				print(" (Timed out... Retrying)", end='')
				try:
					image = imageio.imread(url, format="PNG", pilmode="RGBA")
				except (socket.error, urllib2.URLError):
					print(" (Timed out again. Discarding)", end='')
					image = np.empty([512, 512, 4], dtype="uint8")

			if(layer["overlay"] != ""):
				yearImage = imageio.imread(layer["overlay"])
				if(np.count_nonzero(image) != 0):
					(width, height, depth) = yearImage.shape
					for i in range(width):
						for j in range(height):
							if(yearImage[i][j][3] != 0):
								image[i][j][0] = yearImage[i][j][0]
								image[i][j][1] = yearImage[i][j][1]
								image[i][j][2] = yearImage[i][j][2]
								image[i][j][3] = yearImage[i][j][3]

					images.append(image)
			index += 1
			print("")
	
	imageio.mimsave(name, images, duration=inDuration)

# Example createGIFsFromJSONFile("ajuntaments_radi500_amb_bbox_3857_25831.geojson", "bbox_3857", "EPSG:3857")
def createGIFsFromJSONFile(fileName, bboxParam, idParam, srid, duration):

	with open(fileName) as f:
		data = json.load(f)

		created = 0
		outputFolder = os.path.dirname(os.path.abspath(__file__)) + "/generated/"
		for feature in data['features']:
			bbox = feature['properties'][bboxParam]

			id = created
			if(idParam is not None):
				id = feature['properties'][idParam]
				print("Using json id " + str(id))

			if(not os.path.isfile(outputFolder + str(id) + ".gif")):
				print(outputFolder + str(id) + ".gif file not found. Creating it!")
				createGIF(outputFolder + str(id) + ".gif", 512, 512, srid, bbox, duration)
				print("GIF created: " + outputFolder + str(id) + ".gif")
			else:
				print("GIF " + str(id) + ".gif already created!")
			created += 1

parser = argparse.ArgumentParser(description="Creates a gif from a set of WMS")
parser.add_argument('--file', nargs='?', const=None, default=None, help='The name of the GeoJSON file to be processed')
parser.add_argument('--bboxParam', nargs='?', const=None, default=None, help='The GeoJSON feature bounding box property name')
parser.add_argument('--idParam', nargs='?', const=None, default=None, help='The GeoJSON feature id property to use as the file name')
parser.add_argument('--srid', nargs='?', const=None, default=None, help='The SRID in which the bbox is specified')
parser.add_argument('--bbox', nargs='?', const=None, default=None, help='The bbox to generate the gif from in minLon,minLat,maxLon,maxLat format')
parser.add_argument('--duration', nargs='?', const=None, default=None, help='The duration between frames in seconds')
parser.add_argument('--output', nargs='?', const=None, default=None, help='Output file name')
args = parser.parse_args()

srid = "EPSG:3857"
duration = config.duration

if(args.srid is None):
	print("--srid parameter not present, using default SRID (EPSG:3857)")
else:
	srid = args.srid

if(args.duration is None):
	print("--duration parameter not present, using default frame duration (" + str(config.duration) + ")")
else:
	duration = args.duration


if(args.file is not None):
	print("Processing file " + args.file)
	if(args.bboxParam is not None):
		createGIFsFromJSONFile(args.file, args.bboxParam, args.idParam, srid, duration)
	else:
		print("--bboxParam not present. Cancelling")
else:
	if(args.output is None):
		name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
		print("Using random name " + name + " as output")
	else:
		name = args.output

	if(args.bbox is not None):
		print("Processing the bbox " + args.bbox)
		outputFolder = os.path.dirname(os.path.abspath(__file__)) + "/generated/"
		print("Saving the output in " + outputFolder)
		createGIF(outputFolder + name + ".gif", 512, 512, srid, args.bbox, duration)
		print("GIF created: " + name + ".gif")
	else:
		print("Neither --bbox nor --bboxParam parameters specified")
