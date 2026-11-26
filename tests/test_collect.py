import io,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import collect
class CollectionTests(unittest.TestCase):
 def test_stream_and_truncation(self):
  self.assertEqual(list(collect.iterate(io.StringIO('[{"a":1},{"b":"é"}]'))),[{'a':1},{'b':'é'}])
  with self.assertRaises(ValueError):list(collect.iterate(io.StringIO('[{"a":1}')))
 def test_rights_checked_on_each_media(self):
  raw={'@admin':{'uid':'co123'},'title':[{'value':'Modem'}],'multimedia':[{'legal':{'rights':[{'licence':'All rights reserved'}]},'@processed':{'medium_thumbnail':{'location':'1/preview.jpg'}}}]}
  r=collect.normalize(raw,[{'id':'modems','patterns':['modem']}]);self.assertIsNone(r['image']);self.assertIsNone(r['start']);self.assertEqual(r['makers'],[])
  raw['multimedia'][0]['legal']['rights']=[{'licence':'CC BY-NC-SA 4.0'}]
  self.assertEqual(collect.normalize(raw,[{'id':'modems','patterns':['modem']}])['image']['licence'],'CC BY-NC-SA 4.0')
 def test_mixed_rights_and_path_traversal_rejected(self):
  m={'legal':{'rights':[{'licence':'CC BY-NC-SA 4.0'},{'licence':'All rights reserved'}]},'@processed':{'medium_thumbnail':{'location':'1/test.jpg'}}}
  raw={'@admin':{'uid':'co1'},'title':[{'value':'terminal'}],'multimedia':[m]}
  self.assertIsNone(collect.normalize(raw,[{'id':'custom','patterns':['terminal']}])['image'])
  m['legal']['rights'].pop();m['@processed']['medium_thumbnail']['location']='../test.jpg'
  self.assertIsNone(collect.normalize(raw,[{'id':'custom','patterns':['terminal']}])['image'])
if __name__=='__main__':unittest.main()
