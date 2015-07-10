udl_xml_retriever.py
=================
-----------------
###### Retrieve XML department and subjects information from http://www.udl.cat/generador_xml/
----------------------------------------------------------------------------------------------
## Usage
### Console
```bash
...$ python udl_xml_retriever.py -u username -p password -pt path/to/save/output/files/
```

### Python script
```python
import udl_xml_retriever as uxr

uxr.get_xml(username, password, path)
```