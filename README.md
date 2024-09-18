# NOMAD's pedestrian dynamics extension (PedDyn-ext)

This is a collection of the NOMAD parsers for the following codes:
- [Vadere](https://www.vadere.org)

Notes:
- this plug-in repository follows the same structure as the [plug-in collections](https://github.com/nomad-coe/electronic-parsers) provided by the [NOMAD coe](https://github.com/nomad-coe).
- the structure of the [template](https://github.com/nomad-coe/nomad-parser-plugin-example) of this fork seems to be deprecated. 
- If you are not familiar with schema plug-ins (normalizer plug-ins) and parser plug-ins, please find the [overview of concepts](docs/concepts/plugin_types_and_data_processing.md).


## Testing PedDyn-ext functionalities

The plug-ins of this repository were tested with Python3.9. Please also see the [documentation](docs/index.md)).
PedDyn-ext functionalities are tested 


## Running PedDyn-ext in an oasis


### Step 1: Setup an oasis


> [!WARNING]
> The setup instructions have been changing twice between 06.09.24 and 18.09.24
> https://nomad-lab.eu/prod/v1/docs/howto/oasis/plugins_install.html

It is up to the administrator of the Oasis which option to pick. 


> [!IMPORTANT]
> None of the current setups is currently working for me. 

#### Some comments on using the template repository (no longer available??)
There is a NOMAD instance ("oasis") provided by the pedestrian-dynamics-group on github:
https://github.com/pedestrian-dynamics-HM/nomad-oasis
It is an instantiation of the template repository of the NOMAD organization: https://github.com/FAIRmat-NFDI/nomad-distribution-template.
Note that the instantiation contains a Docker image that was automatically generated when instantiating the template: https://github.com/pedestrian-dynamics-HM/nomad-oasis/pkgs/container/nomad-oasis

Note that the NOMAD documentation is still under progress:
If one follows the instructions from the oasis template (https://github.com/FAIRmat-NFDI/nomad-distribution-template),
one gets the following bug: https://github.com/FAIRmat-NFDI/nomad-distribution-template/issues/22


#### Some comments on the option with the derived Docker image  

In option 2 a derived Docker image is created:
```
FROM gitlab-registry.mpcdf.mpg.de/nomad-lab/nomad-fair:latest

# Switch to root user to install packages to the system with pip
USER root

RUN apt-get update && apt-get -y install git

# Install your plugin here, e.g.:
RUN pip install git+https://github.com/pedestrian-dynamics-HM/nomad-pedestrian-dynamics-extension.git

# Remember to switch back to the 'nomad' user
USER nomad
```

Make sure that you install git and provide the correct URL:

### Step 2: Add the plug-in to a NOMAD Oasis

How to add the plug-in to an oasis, depends on how the oasis has been setup in step 1. 
Please see the [documentation](https://nomad-lab.eu/prod/v1/docs/howto/oasis/plugins_install.html)

Note that the NOMAD-specific configuration files need to be adjusted. This may involve:
- the global nomad.yaml file (contained in the oasis repository/directory)
- the plug-in-specific nomad*.yaml files (contained in THIS repository)







