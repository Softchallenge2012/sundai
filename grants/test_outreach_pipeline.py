import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import outreach_pipeline


class OutreachPipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.prospects_path = Path(self.tmpdir.name) / 'prospects.json'
        self.prospects_path.write_text(json.dumps({
            'metadata': {'purpose': 'test'},
            'prospects': [{
                'id': 'prospect-001',
                'name': 'Alicia Moreno',
                'organization': 'City Food Access Fund',
                'website': 'https://example.org',
                'program_officer': 'Senior Grants Manager',
                'stage': 'new',
                'last_contacted_at': None,
                'next_follow_up_at': None,
                'status': 'pending',
                'notes': [],
                'mission_fit': 'Food access and local nutrition equity',
                'focus_areas': ['food access', 'community nutrition'],
                'priority': 'high',
                'created_at': '2026-11-01T00:00:00Z'
            }]
        }), encoding='utf-8')
        outreach_pipeline.PROSPECTS_PATH = self.prospects_path

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_generate_outreach_email_includes_mission_fit(self):
        email = outreach_pipeline.generate_outreach_email(
            self.prospects_path,
            prospect_id='prospect-001',
            template='intro'
        )
        self.assertIn('City Food Access Fund', email)
        self.assertIn('Food access and local nutrition equity', email)
        self.assertIn('Alicia Moreno', email)

    def test_list_due_followups_filters_soonest_items(self):
        due = outreach_pipeline.list_due_followups(self.prospects_path, days_ahead=30)
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0]['organization'], 'City Food Access Fund')


if __name__ == '__main__':
    unittest.main()
