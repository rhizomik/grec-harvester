#grec-harvester

## Description
***grec-harvester*** is a little script written in python to scrap data in the UdL's (Universitat de Lleida) [GREC website](http://webgrec.udl.cat), a service for note all the research activities developed in the university, and obtain the collected data in RDF Graph or JSON.

## Usage
### Getting requirements
`$ pip install -r requirements.txt`

### Get the data from the console
`$ python grec-harvester.py -f output_file -t {rdf | json} "row_title_1" "row_title_2" ...`

### Get the data from another python script

```python
import grec_harvester

#getting rdf data
rdf_data = rdfize_pub_list(get_pubs_by_row_name("row_name"))
```