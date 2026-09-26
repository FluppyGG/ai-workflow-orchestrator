import unittest
from engine import Engine

class EngineTests(unittest.TestCase):
    def test_classify_and_template(self):
        workflow = {
            "steps": [
                {
                    "name": "segment",
                    "type": "classify",
                    "field": "message",
                    "rules": [{"contains": ["срочно"], "label": "hot"}],
                    "default": "other"
                },
                {
                    "name": "result",
                    "type": "template",
                    "template": "{{name}}/{{segment}}"
                }
            ]
        }
        result = Engine().run(workflow, {"name": "Ivan", "message": "Нужно срочно"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["context"]["result"], "Ivan/hot")

if __name__ == "__main__":
    unittest.main()
