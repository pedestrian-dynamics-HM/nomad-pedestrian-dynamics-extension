import sys
import json
import logging

from nomad.utils import configure_logging
from nomad.datamodel import EntryArchive
from nomad_pedestrian_dynamics_extension.vadere_parser.parser import *

if __name__ == '__main__':
    configure_logging(console_log_level=logging.DEBUG)

    if len(sys.argv) < 2:
        logging.exception(f"File path to archive is missing. Provide the path as CLI argument.")


    archive = EntryArchive()

    data_path = "/home/christina/repos/nomad-pedestrian-dynamics-extension/tests/data/basic_2_density_discrete_ca_2024-08-05_12-33-49.69/postvis.traj"

    VadereParser().parse(data_path, archive, logging)
    json.dump(archive.m_to_dict(), sys.stdout, indent=2)