
# General NOMAD concepts 
This information is based on the FAIRmat Tutorial 12 (https://www.youtube.com/watch?v=mc5kZjeF7KU).

## How to add a data entry in NOMAD

There are two ways how to add a data entry in NOMAD:

![two_options_add_entry.png](../images/two_options_add_entry.png)


Option 1 is that the user uploads an archive with raw data.
A suitable parser is automatically assigned depending on the raw data structure (“matching”). The actual result data is automatically processed from the raw data (“parsing”). 
The result data is processed automatically (“normalizing”). This option is useful when the data from the experiment or simulation needs to be formatted or for generating plots.

Option 2 is that the user fils meta-data into an input mask. The user uploads result data (no raw data!!!). 
The result data can be processed automatically to extract meta data (“normalizing”).


| Option           | Raw data                | Result data                                                       | Meta data                                                                                                     |
|------------------|-------------------------|-------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| 1 Archive upload | is provided by the user | is generated automatically from the raw data (requires: a parser) | is extracted automatically from the processed data  (requires: a normalizer)                                  |
| 2 Schema usage   | -                       | is provided by the user                                           | is provided by the USER   AND/OR  is extracted automatically from the processed data (requires: a normalizer) |




### Option 1: adding a data entry using a schema 

The user selects a schema over the webinterface. The user fill the input mask with data and meta-data. If the schema contains a normalizer meta-data is automatically generated from the user input when saving the  user input.

Schemas are available as "built-in schema" on the web-interface. Here is an example schema ("XRay Diffraction"):

![schema_web_browser.png](../images/schema_web_browser.png)

The experimental data is added directly in the data entry. When clicking "save" the data is further processed if there is a normalizer attached to the schema:

![schema_data_upload.png](../images/schema_data_upload.png)

### Option 2: adding a data entry using a parser

The user provides a data archive

![data_archive.png](../images/data_archive.png)




Important: the normalizer is executed after the parsing process: 

![fairmat_tutorial_12_interplay_plugins.png](../images/fairmat_tutorial_12_interplay_plugins.png)

## Schemas
Schemas define the structure of data:

![fairmat_tutorial_12_schemas.png](../images/fairmat_tutorial_12_schemas.png)






### How to define schemas

Schemas can be specified as *.yaml file OR as Python class. We use Python classes.
In Python a schema is defined by implementing the MSection interface:
![fairmat_tutorial_12_implementation.png](../images/fairmat_tutorial_12_implementation.png)


NOMAD provides interfaces for schemas for empirical data and simulation data.

We implement these interfaces for pedestrian dynamics specific applications:
- empirical research: laboratory experiments, field observations
- simulation studies: conducted with the Optimal Steps Model, conducted with the Social Force Model, ... 

![fairmat_tutorial_12_abstraction.png](../images/fairmat_tutorial_12_abstraction.png)

![fairmat_tutorial_12_uml_metainfo.png](../images/fairmat_tutorial_12_uml_metainfo.png)




Some images are snapshots from FAIRmat Tutorial 12 (https://www.youtube.com/watch?v=mc5kZjeF7KU)
