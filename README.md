# NOMAD's pedestrian dynamics extension 

This is a collection of the NOMAD parsers for the following codes:
- [Vadere](https://www.vadere.org)

This plug-in parses simulation output from a Vadere simulation (*.scenario, postvis.traj) into a dictionary.
In addition, it computes macroscopic quantities from the microscopic data:


![img.png](docs/images/macroscopic_qunatities.png)




This plug-in provides a NOMAD parser, a NOMAD schema and normalizing functionalities.
If you are not familiar with these concepts, please read our [overview of NOMAD concepts](docs/concepts/plugin_types_and_data_processing.md).


### Re-using existing NOMAD plug-ins

NOMAD provides several plug-ins for ["computational data"](https://nomad-lab.eu/prod/v1/docs/examples/computational_data/schema_plugins.html) that are data produced by simulators.
This plug-in is based on the plug-in ```nomad-schema-plugin-run```. 
The source code of this plug-in is publicly available on [github](https://github.com/nomad-coe/nomad-schema-plugin-run) 
and under the [Python package registry](https://pypi.org/project/nomad-schema-plugin-run/).





### Developing and testing the plug-in locally (this does not require a running NOMAD Oasis)
This plug-in was tested with Python3.9.

To test the plug-in you need to install the Python package ```nomad-lab```. The plug-in ```nomad-schema-plugin-run``` requires a 
nomad-lab version that is not published under the Python package index registry (see the [issue](https://github.com/pedestrian-dynamics-HM/nomad-pedestrian-dynamics-extension/issues/3)

We recommend the following steps to avoid dependency conflicts:

1. Create a virtual Python3.9 environment and activate it:
```
python3.9 -m venv myvirtualenv
source myvirtualenv/bin/activate
```
2. Install ```nomad-lab``` using NOMAD's internal registry:
```
pip install https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/files/472e0cb3bc16d51251a84464686db9e1ce80791a945ffa5faa3e69ee869b6012/nomad-lab-1.3.6.dev41+g0347838e4.tar.gz
```
3. Install the plug-in 
```
pip install nomad-schema-plugin-run
```
Note: the automatic dependency handling (step 3) would try to install nomad-lab over the Python package registry.
Because the required nomad-lab version is not published under the Python package registry the dependency handling fails.
We prevent from this by manually installing nomad-lab in step 2.

After your system setup simply run the *.py tests in [tests directory](tests).
Please also see the [documentation](docs/index.md).


### Running the plug-ins in a NOMAD oasis

Please follow the instructions from: https://nomad-lab.eu/prod/v1/docs/howto/oasis/plugins_install.html

> [!WARNING]
> The setup instructions seems to be constantly changing.

I used the option with the derived Docker image.
Setup an oasis without plug-ins (detailed information can be found in the [documentation-1](https://nomad-lab.eu/prod/v1/docs/howto/oasis/install.html)):

Download the [nomad-oasis.zip](https://nomad-lab.eu/prod/v1/docs/assets/nomad-oasis.zip)
```
unzip nomad-oasis.zip
cd nomad-oasis
sudo chown -R 1000 .volumes
docker compose pull
```

Create the derived Docker image. Copy the following content into an empty Dockerfile (textfile named "Dockerfile") 

```
FROM gitlab-registry.mpcdf.mpg.de/nomad-lab/nomad-fair:latest

# Switch to root user to install packages to the system with pip
USER root

# for installing a python repo from github
RUN apt-get update && apt-get -y install git

RUN pip install --upgrade pip

# installs nomad version 1.3.6 - which is required by the nomad-schema-plugin-run depencency. 
# Automatic dependency resolving is not working! 
# REPLACE the following line as soon as a stable nomad version is available
RUN pip install https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/files/472e0cb3bc16d51251a84464686db9e1ce80791a945ffa5faa3e69ee869b6012/nomad-lab-1.3.6.dev41+g0347838e4.tar.gz

# Install your plugin here, e.g.:
RUN pip install git+https://github.com/pedestrian-dynamics-HM/nomad-pedestrian-dynamics-extension.git@main

# Remember to switch back to the 'nomad' user
USER nomad
```

Replace the Docker image "gitlab-registry.mpcdf.mpg.de/nomad-lab/nomad-fair:latest" by the derived image in nomad-oasis/docker-compose.yaml:

```
  worker:
    restart: unless-stopped
    #image: gitlab-registry.mpcdf.mpg.de/nomad-lab/nomad-fair:latest
    image: nomad-with-plugins

  north:
    restart: unless-stopped
    #image: gitlab-registry.mpcdf.mpg.de/nomad-lab/nomad-fair:latest
    image: nomad-with-plugins

  app:
    restart: unless-stopped
    #image: gitlab-registry.mpcdf.mpg.de/nomad-lab/nomad-fair:latest
    image: nomad-with-plugins
```
Now the image needs to be built by the following command:
```
docker build -t nomad-with-plugins .
```
This command builds the docker image from the Dockerfile in the current working
directory. 

Start the oasis
```
docker compose up -d
```
Open http://localhost/nomad-oasis in your browser.

#### Uploading entries

One can upload a single simulation run or a collection of simulation runs. 
This repository contains *.zip-files for testing both functionalities:
- [archive of a single simulation run](tests/data/basic_2_density_discrete_ca_2024-09-23_15-52-24.887.zip)
- [archive with multiple simulation runs](tests/data/several_simulation_runs.zip)

The following snapshot was taken after uploading the two archives to an empty oasis:

![single_and_multiple_runs.png](docs/images/single_and_multiple_runs.png)









