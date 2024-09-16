
# General NOMAD concepts 
This information is based on the FAIRmat Tutorial 12 (https://www.youtube.com/watch?v=mc5kZjeF7KU).

## Schemas
Schemas define the structure of data:

![fairmat_tutorial_12_schemas.png](../images/fairmat_tutorial_12_schemas.png)

Schemas can be specified as *.yaml file OR as Python class. We use Python classes.
In Python a schema is defined by implementing the MSection interface:
![fairmat_tutorial_12_implementation.png](../images/fairmat_tutorial_12_implementation.png)


NOMAD provides interfaces for schemas for empirical data and simulation data.

We implement these interfaces for pedestrian dynamics specific applications:
- empirical research: laboratory experiments, field observations
- simulation studies: conducted with the Optimal Steps Model, conducted with the Social Force Model, ... 

![fairmat_tutorial_12_abstraction.png](../images/fairmat_tutorial_12_abstraction.png)

![fairmat_tutorial_12_uml_metainfo.png](../images/fairmat_tutorial_12_uml_metainfo.png)

## Data processing 

There are different types of plug-ins that process data:
- Parsers: parse raw data. 
- Normalizers: parse processed data. 

The normalizing process is executed after the parsing process: 

![fairmat_tutorial_12_interplay_plugins.png](../images/fairmat_tutorial_12_interplay_plugins.png)

All images are snapshot from FAIRmat Tutorial 12 (https://www.youtube.com/watch?v=mc5kZjeF7KU)
