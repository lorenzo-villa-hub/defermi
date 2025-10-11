#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 10:24:50 2023

@author: villa
"""
import json

from defermi.tools.materials_project import MPDatabase

from defermi.testing.core import DefermiTest
from defermi.testing.structure import StructureTest

class TestMPDatabase(DefermiTest):

    def setUp(self):
        self.mpd = MPDatabase('mp-149')

    def test_get_structure(self):
        structure = self.mpd.get_structure()
        StructureTest().assert_Structure_equal( structure , self.structure )

    def test_get_entries(self):
        entries = MPDatabase().get_entries('SiO2')
        for entry in entries:
            if entry.data['task_id'] == 'mp-1245253':
                actual = entry.energy
                desired = -743.3118525
                self.assertEqual(actual, desired)
        
