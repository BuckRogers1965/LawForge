import sys
import pytest

# Add the 'docs' directory to the python path to find the 'lawforge' module
sys.path.insert(0, 'docs')

from lawforge.deriver import derive_law_from_postulate

def test_einstein_derivation():
    result = derive_law_from_postulate("E ~ m")
    assert "E = k*c**2*m" in result.replace(" ", "")

def test_newton_gravity_derivation():
    result = derive_law_from_postulate("F ~ M1*M2/r**2")
    assert "F=k*G*M1*M2/r**2" in result.replace(" ", "")

# Add more tests here...
