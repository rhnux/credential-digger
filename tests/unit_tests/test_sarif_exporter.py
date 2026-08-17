import unittest
from credentialdigger.export.sarif_exporter import export_to_sarif


class TestSarifExporter(unittest.TestCase):
    def setUp(self):
        self.discoveries = [
            {
                'id': 1,
                'file_name': 'test.py',
                'commit_id': 'abc1234',
                'line_number': 42,
                'snippet': 'password = "secret_password_123"',
                'repo_url': 'https://github.com/user/repo',
                'rule_id': 1,
                'state': 'new',
                'timestamp': '2023-01-01T00:00:00Z'
            }
        ]
        self.rules = [
            {
                'id': 1,
                'regex': 'password\\s*=\\s*["\'].*["\']',
                'category': 'password',
                'description': 'Hardcoded password detection'
            }
        ]

    def test_export_to_sarif_basic(self):
        sarif = export_to_sarif(self.discoveries, self.rules)
        self.assertEqual(sarif.get('version'), '2.1.0')
        self.assertEqual(sarif.get('$schema'), 'https://json.schemastore.org/sarif-2.1.0.json')
        self.assertIn('runs', sarif)
        self.assertEqual(len(sarif['runs']), 1)

        run = sarif['runs'][0]
        driver = run['tool']['driver']
        self.assertEqual(driver['name'], 'Credential Digger')
        self.assertEqual(len(driver['rules']), 1)
        self.assertEqual(driver['rules'][0]['id'], '1')

        results = run['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['ruleId'], '1')
        self.assertEqual(results[0]['ruleIndex'], 0)
        self.assertEqual(results[0]['locations'][0]['physicalLocation']['artifactLocation']['uri'], 'test.py')
        self.assertEqual(results[0]['locations'][0]['physicalLocation']['region']['startLine'], 42)

    def test_export_to_sarif_empty(self):
        sarif = export_to_sarif([], [])
        self.assertEqual(sarif.get('version'), '2.1.0')
        self.assertEqual(len(sarif['runs'][0]['results']), 0)


if __name__ == '__main__':
    unittest.main()
