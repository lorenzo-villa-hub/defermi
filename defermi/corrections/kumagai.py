
import warnings
import os.path as op
import importlib
import matplotlib.pyplot as plt
import math


from pymatgen.io.vasp.outputs import Outcar, Vasprun

from pymatgen.analysis.defects.corrections.kumagai import _check_import_pydefect 
from pymatgen.analysis.defects.utils import CorrectionResult, get_zfile

from ..tools.structure import is_site_in_structure_coords
from ..structure import defect_finder

from pathlib import Path



    
def get_kumagai_correction(
                        defect_path,
                        bulk_path,
                        charge,
                        dielectric_tensor,
                        initial_structure=False,
                        get_correction_data=True,
                        get_plot=True,
                        **kwargs):
    """
    Compute Kumagai corrections (extended FNV scheme) from VASP calculation paths.

    Parameters
    ----------
    defect_path : str
        Path of defect calculation with vasprun.xml and OUTCAR files.
    bulk_path : str
        Path of bulk calculation with vasprun.xml and OUTCAR files.
    charge : int
        Charge of defect calculation
    dielectric_tensor : int,float 3x1 array or 3x3 array
        Dielectric tensor (or constant). Types accepted are int,float 3x1 array or 3x3 array.
    initial_structure : bool
        Use initial structure of defect calculation for correction computation.
        Useful to compute correction on unrelaxed structure.
    get_correction_data : bool
        Return pymatgen's CorrectionResult object. If False only the correction value is returned.
    get_plot : bool
        Get Matplotlib object with plot. The default is False. 
    kwargs : dict
        Kwargs to pass to pydefect `make_efnv_correction`
    
    Returns
    -------
    correction, ax : tuple
        CorrectionResult object if get_correction_data is set to True, else just the float with correction value, matplotlib axis object  
        
    """
    defect_structure = _get_structure_with_pot_pmg(defect_path,initial_structure=initial_structure)
    bulk_structure = _get_structure_with_pot_pmg(bulk_path,initial_structure=False)
    correction = get_kumagai_correction_from_structures(
                                            defect_structure_with_potentials=defect_structure,
                                            bulk_structure_with_potentials=bulk_structure,
                                            charge=charge,
                                            dielectric_tensor=dielectric_tensor,
                                            **kwargs)
    
    corr = correction if get_correction_data else correction.correction_energy
    if get_plot:
        from pydefect.corrections.site_potential_plotter import SitePotentialMplPlotter
        SitePotentialMplPlotter.from_efnv_corr(
                                            title=defect_structure.composition,
                                            efnv_correction=correction.metadata['efnv_corr']
                                            ).construct_plot()
        ax = plt.gca()
        return corr, ax
    else:
        return corr 



def get_kumagai_correction_from_structures(
                                        defect_structure_with_potentials,
                                        bulk_structure_with_potentials,
                                        charge,
                                        dielectric_tensor,
                                        **kwargs):
    """
    Get Kumagai (extended FNV) correction from Structure objects with 
    site potentials stored into site_properties. Not recommended to use
    directly, refer to `get_kumagai_correction`.
    """
    dielectric_tensor = _convert_dielectric_tensor(dielectric_tensor)
    correction =  _get_efnv_correction_pmg_fixed(
                            charge=charge,
                            defect_structure=defect_structure_with_potentials,
                            bulk_structure=bulk_structure_with_potentials,
                            dielectric_tensor=dielectric_tensor,
                            **kwargs)
    return correction




def _get_efnv_correction_pmg_fixed(
    charge,
    defect_structure,
    bulk_structure,
    dielectric_tensor,
    **kwargs):
    """
    Fixed code from `pymatgen.analysis.defects.corrections.kumagai.get_efnv_correction`,
    defect_potentials and site_potentials variables were inverted.
    
    Returns the Kumagai/Oba EFNV correction for a given defect.

    Parameters
    ----------
    charge : int or float
        Charge of the defect.
    defect_structure : Structure
        Defect structure.
    bulk_structure : Structure
        Bulk structure.
    dielectric_tensor : np.array
        Dielectric tensor.
    kwargs : dict
        Kwargs to pass to `make_efnv_correction`.
    """
    from pydefect.analyzer.calc_results import CalcResults
    from pydefect.cli.vasp.make_efnv_correction import make_efnv_correction

    # ensure that the structures have the "potential" site property
    defect_potentials = [site.properties["potential"] for site in defect_structure]
    bulk_potentials = [site.properties["potential"] for site in bulk_structure]

    defect_calc_results = CalcResults(
        structure=defect_structure,
        energy=math.inf,
        magnetization=math.inf,
        potentials=defect_potentials,
    )
    bulk_calc_results = CalcResults(
        structure=bulk_structure,
        energy=math.inf,
        magnetization=math.inf,
        potentials=bulk_potentials,
    )

    efnv_corr = make_efnv_correction(
        charge=charge,
        calc_results=defect_calc_results,
        perfect_calc_results=bulk_calc_results,
        dielectric_tensor=dielectric_tensor,
        **kwargs,
    )

    return CorrectionResult(
        correction_energy=efnv_corr.correction_energy,
        metadata={"efnv_corr": efnv_corr},
    )


def _get_structure_with_pot_pmg(directory,initial_structure=False):
    """
    Modified function from pymatgen.analysis.defects-corrections.kumagai 
    to allow for initial structure import

    Reads vasprun.xml and OUTCAR files in a directory.

    Parameters
    ----------
    directory : str
        Directory containing vasprun.xml and OUTCAR files.

    Returns
    -------
    structure : Structure
        Structure with "potential" site property.
    """
    _check_import_pydefect()
    from pydefect.analyzer.calc_results import CalcResults

    d_ = Path(directory)
    f_vasprun = get_zfile(d_, "vasprun.xml")
    f_outcar = get_zfile(d_, "OUTCAR")
    vasprun = Vasprun(f_vasprun,parse_dos=False,parse_potcar_file=False,parse_eigen=False)
    outcar = Outcar(f_outcar)

    structure = vasprun.structures[0] if initial_structure else vasprun.final_structure

    calc = CalcResults(
        structure=structure,
        energy=outcar.final_energy,
        magnetization=outcar.total_mag or 0.0,
        potentials=[-p for p in outcar.electrostatic_potential],
        electronic_conv=vasprun.converged_electronic,
        ionic_conv=vasprun.converged_ionic,
    )

    return calc.structure.copy(site_properties={"potential": calc.potentials})


def _convert_dielectric_tensor(dielectric):
    import numpy as np
    if not type(dielectric) in [float,int]:
        dielectric = np.array(dielectric)
        if dielectric.shape == (3,):
            dielectric = np.diag(dielectric)
        elif dielectric.shape != (3, 3):
            raise ValueError("Dielectric tensor can be int/float, a 3x1 array with diagonal components of dielectric tensor, or 3x3 matrix")
    else:
        dielectric = np.eye(3) * dielectric

    return dielectric


