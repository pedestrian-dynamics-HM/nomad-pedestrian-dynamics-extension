import os.path
from logging import Logger

import pytest
from nomad.client import normalize_all, parse
from nomad.datamodel import EntryArchive
import sys


from nomad_pedestrian_dynamics_extension.vadere_parser import ExampleParserChristina


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

def test_matching():

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