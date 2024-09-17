# NOMAD's pedestrian dynamics extension (PedDyn-ext)
This NOMAD plug-in is a fork of the NOMAD template: https://github.com/nomad-coe/nomad-parser-plugin-example

This python package contains schema plug-ins and parser plug-ins (see [plugin_types_and_data_processing.md](docs/concepts/plugin_types_and_data_processing.md) for an introduction to these plug-in types).



## Structure of this repository

Each parser and normalizer is realized as individual sub-package as shown in the FAIRmat Tutorial 9 (https://www.youtube.com/watch?v=hZZtxXMoSq8, 07:05 - 09:30).
Each sub-package contains a `nomad_plugin.yaml` file that contains the metadata of the plug-in.

Note: when you change modules or class names, make sure to update the `nomad_plugin.yaml` accordingly!



## System requirements

See the NOMAD documentation. The plug-ins of this repository were tested with Python3.9 (see [index.md](docs/index.md)) 


## How to install PedDyn-ext to an oasis

### Step 1: Setup an oasis

There are three options available how plug-ins can be installed in a NOMAD Oasis: see https://nomad-lab.eu/prod/v1/docs/howto/oasis/plugins_install.html
It is up to the administrator of the Oasis which option to pick. 

#### Some comments on option 1
There is a NOMAD instance ("oasis") provided by the pedestrian-dynamics-group on github:
https://github.com/pedestrian-dynamics-HM/nomad-oasis
It is an instantiation of the template repository of the NOMAD organization: https://github.com/FAIRmat-NFDI/nomad-distribution-template.
Note that the instantiation contains a Docker image that was automatically generated when instantiating the template: https://github.com/pedestrian-dynamics-HM/nomad-oasis/pkgs/container/nomad-oasis

Note that the NOMAD documentation is still under progress:
If one follows the instructions from the oasis template (https://github.com/FAIRmat-NFDI/nomad-distribution-template),
one gets the following bug: https://github.com/FAIRmat-NFDI/nomad-distribution-template/issues/22


### Step 2: Add the plug-in to a NOMAD Oasis

How to add the plug-in to an oasis, depends on how the oasis has been setup in step 1. 
Please see the documentation: https://nomad-lab.eu/prod/v1/docs/howto/oasis/plugins_install.html

Note that the NOMAD-specific configuration files need to be adjusted. This may involve:
- the global nomad.yaml file (contained in the oasis repository/directory)
- the plug-in-specific nomad*.yaml files (contained in THIS repository)




