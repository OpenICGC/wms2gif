# wms2gif
A tool to create a gif from a set of wms layers

## Requirements 
Python 2.7.4 or newer
Node.js to use as a service

## Configuration<a name="configuration"></a>
The WMS endpoints that will be fetched are found in a configuration file in python [_config.py_](config.py) that contains the following elements:

* __layerDefinitions__ is a map with the WMS endpoint URL as the key and an array of _layerObject_ as the value. Each _layerObject_ is a map with _name_ and _overlay_ properties. _name_ is the layer name in the WMS endpoint and _overlay_ is the relative path to an image that will be alpha-blended with the WMS response. View the [_config.py_](config.py) file for an example
* __duration__ is the time in seconds between each image in the resulting gif

## Running the python script
The gif generation is done by the [_gifGenerator.py_](gifGenerator.py) python script. It has two working modes: an __interactive__ mode where a bounding box is specified and a __bulk__ mode where a GeoJSON file is processed to generate Gifs from different positions

### Installing the dependencies
Just run `pip install requirements` and the [numpy](https://www.scipy.org/scipylib/download.html) and [imageio](https://pypi.python.org/pypi/imageio) packages will be installed

### Script parameters

You can run `python gifGenerator.py -h` to see a reduced view of this information
* __--file__ The name of the GeoJSON file to be processed. Used in __bulk__ mode
* __--bboxParam__ The name of the GeoJSON feature property where the bounding box is specified. __Required__ in __bulk__ mode
* __--idParam__ The name of the GeoJSON feature property where the id is specified. Used in __bulk__ mode. If none is present, an autoincrementing id is used.
* __--bbox__ The bounding box requested in the WMS requests to create the GIF in the xMin,yMin,xMax,yMax format. Used in __interactive__ mode.
* __--output__ The name (without extension) of the output file. Used in __interactive__ mode. 
* __--duration__ The duration in seconds of the gif. Used in __bulk__ and __interactive__ modes. If not present, the one in the configuration is used
* __--srid__ The SRID used by the bounding box. Used in __bulk__ and __interactive__ modes. If not present, EPSG:3857 is used

#### Bulk mode example:
Given the following GeoJSON called _bboxs.json_:
```json
{
    "type": "FeatureCollection", 
    ...
    "features":[
        {
            "type": "Feature", 
            "properties": {
                "id": "0", 
                "bbox_3857": "223298.192,5076488.639,223983.217,5077308.063" 
            } 
        },
        ...
    ]
}
```
we can run the following command to generate a gif for each feature
```
python gifGenerator.py --file bboxs.json -- bboxParam bbox_3857 --idParam id
```
The generated gifs will be written to the _generated_ folder.

#### Interactive mode example:
Running the following command
```
python gifGenerator.py --bbox "205000.110935124,5176119.97098418,206000.110935124,5177119.97098418"
```
will generate a gif with a random name in the _generated_ folder
## Running as a service
This repo includes a Node Express server implementation that listens to a request, generates a GIF from a specified bounding box and sends an email with the link to download it to the given email.

### Configuration
The [_config.js_](config.js) file contains the configuration of the service.
* __serverURL__ is the base server URL used to build the email download link
* __pathMainWeb__ is the folder where the service is running. http://_serverURL_/_pathMainWeb_/ will be used as the service entry point.
* __mailServer__ is the address of the mail server used to send the email to the user
* __emailFrom__ is the email address that will be used as a sender in the email
The [_/templates/email.html_](templates/email.html) contains the email text that will be sent to the user once the GIF generation is finished. The _{_FILE_PATH_}_ string will be replaced by the download URL.

### Using the service
The service is listening for GET requests in the _pathMainWeb_ folder and needs _bbox_ and _email_ parameters

The following request `http://_serverURL_/_pathMainWeb_/?bbox=&a@b.com` would generate a GIF from the given bbox and send an email with a download link to a@b.com when finishes.

Take into account that the service is using the script configuration file to generate the GIF. The [python script configuration](#configuration) section details its content.

