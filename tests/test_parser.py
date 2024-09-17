import os.path
from logging import Logger

import pytest
from nomad.client import normalize_all, parse
from nomad.datamodel import EntryArchive
import sys


from nomad_pedestrian_dynamics_extension.vadere_parser import *


def test_parser_2():
    archive = EntryArchive()
    parser = ExampleParserChristina()
    logger = Logger("test")

    test_file = os.path.join(
        os.path.dirname(__file__), 'data', 'test.example-format.txt'
    )
    parser.parse(test_file, archive, logger)

    normalize_all(archive)

    assert archive.data.pattern.tolist() == [
        [1.0, 0.0, 1.0],
        [1.0, 1.0, 1.0],
        [1.0, 0.0, 1.0],
    ]

    print("done")

def test():

    test_file = os.path.join(
        os.path.dirname(__file__), 'data', 'test.example-format.txt'
    )

    # match and run the parser
    archive = parse(test_file)
    # run all normalizers
    normalize_all(archive)

    # get the 'main section' section_run as a metainfo object
    section_run = archive.section_run[0]

    # get the same data as JSON serializable Python dict
    python_dict = section_run.m_to_dict()



def test_example():
    archive = EntryArchive()
    logger = Logger("test")
    data_path = os.path.join(os.path.dirname(__file__), "data", "example.out")

    data_path = os.path.join(os.path.dirname(__file__), "data", "basic_2_density_discrete_ca_2024-08-05_12-33-49.69" , "postvis.traj")
    parser = VadereParser()
    parser.parse(data_path, archive, logger)

    sim = archive.data
    assert len(sim.model) == 2
    assert len(sim.output) == 2
    assert archive.workflow2.x_example_magic_value == 42