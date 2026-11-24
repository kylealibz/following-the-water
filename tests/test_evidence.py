"""Checks protecting evidence roles, missingness and quantitative symbology."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_evidence import build,symbol_diameter


class EvidenceTests(unittest.TestCase):
    def test_locations_are_not_invented(self):
        places,readings=build()
        self.assertEqual(len(readings),8)
        self.assertEqual(sum(r['geonames_reference_id'] is None for r in readings),3)
        self.assertEqual(len(places['features']),9)
        self.assertEqual(sum(f['properties']['reported_do_mg_l'] is None for f in places['features']),4)
        self.assertTrue(all(r['sample_datetime'] is None for r in readings))
        by_id={r['geonames_reference_id']:r['reported_value'] for r in readings if r['geonames_reference_id']}
        for f in places['features']:
            self.assertEqual(f['properties']['reported_do_mg_l'],by_id.get(f['properties']['geonames_id']))

    def test_circle_area_encodes_value(self):
        self.assertAlmostEqual((symbol_diameter(1.28)/symbol_diameter(6.19))**2,1.28/6.19,places=5)
        with self.assertRaises(ValueError):symbol_diameter(-1)


if __name__=='__main__':unittest.main()
