import json
from var_annot.ensembl import get_vep_data, vep_post, fetch_endpoint_post


def test_fetch_endpoint_post():
    server = "https://grch37.rest.ensembl.org/"
    endpoint = "variation/homo_sapiens"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    data_json = json.dumps({"ids": ["rs6603781"]})
    actual = fetch_endpoint_post(server=server, request=endpoint, data=data_json, headers=headers)
    assert type(actual) == dict, "Unable to connect to Ensembl."


def test_vep_post():
    data_id = "ids"
    data_list = ["rs6603781"]
    endpoint = "variation/homo_sapiens"
    server = "https://grch37.rest.ensembl.org/"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    limit = 200
    outfile = None
    actual = vep_post(
        data_id=data_id,
        data_list=data_list,
        endpoint=endpoint,
        server=server,
        headers=headers,
        limit=limit,
        outfile=outfile,
    )
    assert type(actual) == dict, "Unable to connect to Ensembl."


def test_get_vep_data():
    pass
