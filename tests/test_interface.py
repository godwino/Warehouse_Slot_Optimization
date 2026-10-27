import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

class InterfaceTests(unittest.TestCase):
 def test_all_sections_render(self):
  at=AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app/streamlit_app.py'),default_timeout=30).run()
  for page in ['Overview','Place a New Product','Improve Existing Positions','Follow a Sample Assignment','QA Review and Move Plan','Data and Validation','Stakeholder Brief']:
   with self.subTest(page=page):
    at.sidebar.radio[0].set_value(page).run()
    self.assertEqual(list(at.exception),[])
