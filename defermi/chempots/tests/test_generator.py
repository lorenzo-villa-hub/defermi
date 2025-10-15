

from defermi.chempots.generator import generate_chempots_from_mp, generate_pressure_reservoirs_from_precursors
from numpy.testing import assert_allclose

def test_generate_chempots_from_mp():

    res = generate_chempots_from_mp('BaTiO3')
    
    actual = res['O-poor']['Ba']
    desired = -2.93861
    assert_allclose(actual,desired)

    actual = res['O-middle']['Ti']
    desired = -13.568998
    assert_allclose(actual,desired)

    actual = res['O-rich']['O']
    desired = -4.947961
    assert_allclose(actual,desired)

    res = generate_chempots_from_mp('BaTiO3',element='Ti')
    actual = res['Ti-middle']['Ti']
    desired = -13.615674
    assert_allclose(actual,desired)

    chempots = generate_chempots_from_mp('BaTiO3',element='Ba-poor')
    actual = chempots['Ba']
    desired = -8.584461
    assert_allclose(actual,desired)


def test_generate_pressure_reservoirs_from_precursors():

    res = generate_pressure_reservoirs_from_precursors(
                                    precursors=['BaO','TiO2'],
                                    temperature=800,
                                    pressure_range=(1e-20,1e10),
                                    npoints=50)
    
    actual = res[1e-20]['Ba'] , res[1e10]['O']
    desired = -5.12537436, -5.007791
    assert_allclose(actual,desired)

    assert len(res) == 50

    res = generate_pressure_reservoirs_from_precursors(precursors='SiO2',temperature=800)
    actual = res[1e-20]['O'] , res[1e10]['Si']
    desired = -7.388847 , -15.10720972

