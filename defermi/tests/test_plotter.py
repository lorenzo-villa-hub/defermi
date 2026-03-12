#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: villa
"""
import matplotlib.pyplot as plt
import pandas as pd
from defermi.analysis import DefectsAnalysis

from defermi.testing.core import DefermiTest

def get_preset_case():
    df = pd.DataFrame([
    {'name': 'Int_O', 'charge': -2.0, 'multiplicity': 2, 'energy_diff': 2.1, 'bulk_volume': 800.0},
    {'name': 'Int_O', 'charge': 0.0, 'multiplicity': 2, 'energy_diff': 1.6, 'bulk_volume': 800.0},
    {'name': 'Pol_Ti', 'charge': -1.0, 'multiplicity': 1, 'energy_diff': 10.0, 'bulk_volume': 800.0},
    {'name': 'Sub_Fe_on_Sr', 'charge': 0.0, 'multiplicity': 1, 'energy_diff': -0.5, 'bulk_volume': 800.0},
    {'name': 'Sub_Fe_on_Sr', 'charge': 1.0, 'multiplicity': 1, 'energy_diff': -1.1, 'bulk_volume': 800.0},
    {'name': 'Sub_Fe_on_Ti', 'charge': -2.0, 'multiplicity': 1, 'energy_diff': 7.5, 'bulk_volume': 800.0},
    {'name': 'Sub_Fe_on_Ti', 'charge': -1.0, 'multiplicity': 1, 'energy_diff': 6.5, 'bulk_volume': 800.0},
    {'name': 'Vac_O', 'charge': 0.0, 'multiplicity': 1, 'energy_diff': 10.8, 'bulk_volume': 800.0},
    {'name': 'Vac_O', 'charge': 2.0, 'multiplicity': 1, 'energy_diff': 7.0, 'bulk_volume': 800.0},
    {'name': 'Vac_O;Vac_Sr', 'charge': -2.0, 'multiplicity': 1, 'energy_diff': 19.7, 'bulk_volume': 800.0},
    {'name': 'Vac_O;Vac_Sr', 'charge': 0.0, 'multiplicity': 1, 'energy_diff': 16.0, 'bulk_volume': 800.0},
    {'name': 'Vac_O;Vac_Sr', 'charge': 2.0, 'multiplicity': 1, 'energy_diff': 15.7, 'bulk_volume': 800.0},
    {'name': 'Vac_Sr', 'charge': -2.0, 'multiplicity': 1, 'energy_diff': 8.0, 'bulk_volume': 800.0},
    {'name': 'Vac_Sr', 'charge': 0.0, 'multiplicity': 1, 'energy_diff': 7.8, 'bulk_volume': 800.0}])
    vbm = 0 # eV
    band_gap = 2 # eV
    chempots = {'O': -4.95, 'Sr': -2, 'Ti':-8, 'Fe':-8.5}
    bulk_dos = {'m_eff_e': 0.5, 'm_eff_h': 0.4} # effective masses
    da = DefectsAnalysis.from_dataframe(df,band_gap=band_gap,vbm=vbm)
    return da, chempots , bulk_dos



class TestPlotter(DefermiTest):

    @classmethod
    def setUpClass(cls):
        da, chempots, bulk_dos = get_preset_case()
        cls.da = da
        cls.chempots = chempots
        cls.bulk_dos = bulk_dos 

    def test_plot_binding_energies(self):
        return self.da.plot_binding_energies()

    def test_plot_ctl(self):
        return self.da.plot_ctl()

    def test_plot_formation_energies(self):
        return self.da.plot_formation_energies(self.chempots)

    def test_plot_brouwer_diagram(self):
        return self.da.plot_brouwer_diagram(
                        bulk_dos=self.bulk_dos,
                        temperature=1000,
                        fixed_concentrations={'Fe':1e16},
                        precursors={'SrO':-10,'TiO2':-22},
                        oxygen_ref=-5)
  
    def test_plot_doping_diagram(self):
        return self.da.plot_doping_diagram(
                        variable_defect_specie='Fe',
                        concentration_range=(1e05,1e20),
                        chemical_potentials=self.chempots,
                        bulk_dos=self.bulk_dos,
                        temperature=1000)
    
    def test_show_plots(self):
        plt.show()
