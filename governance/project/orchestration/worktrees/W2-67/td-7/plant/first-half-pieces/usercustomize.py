"""W2-67 batch 7's plant: the fault named by this folder's name, from ../lib/td7_plants.py (throwaway)."""
import importlib.util
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("td7_plants", os.path.join(os.path.dirname(_here), "lib", "td7_plants.py"))
_plants = importlib.util.module_from_spec(_spec)
sys.modules["td7_plants"] = _plants
_spec.loader.exec_module(_plants)
_plants.install(os.path.basename(_here), _here)
