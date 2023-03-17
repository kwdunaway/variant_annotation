#!/usr/bin/env python
"""
Group of functions which enable Ensembl interaction.
"""

import json
import requests
from typing import Optional
from http import HTTPStatus
from var_annot.exception import PostError


def get_vep_data(
    hgvs_list: list,
    hgvs_infile: Optional[str] = None,
    hgvs_outfile: Optional[str] = None,
    ids_infile: Optional[str] = None,
    ids_outfile: Optional[str] = None,
) -> dict:
    """
    Gets the VEP data using API calls and/or local files.

    :param hgvs_list: List of HGVS notations. Ex: 'X:g.71341908T>C'
    :param hgvs_infile: Loads HGVS data from this JSON file.
    :param hgvs_outfile: Writes HGVS data to this JSON file path.
    :param ids_infile: Loads Variant ID data from this JSON file.
    :param ids_outfile: Writes Variant ID data to this JSON file path.
    :return: Dict of VEP data
    """
    if hgvs_infile:
        hgvs_data = json.load(open(hgvs_infile))
    else:
        hgvs_data = vep_post(
            data_id="hgvs_notations",
            data_list=hgvs_list,
            endpoint="vep/human/hgvs",
            limit=300,
            outfile=hgvs_outfile,
        )

    vep_data = {}
    ids_mapping = {}
    # Map variant_ids in hgvs_data
    for var_data in hgvs_data:
        hgvs_key = var_data["input"]
        vep_id = None
        if "colocated_variants" in var_data:
            for col_var in var_data["colocated_variants"]:
                if col_var["id"].startswith("rs"):
                    vep_id = col_var["id"]
                elif not vep_id:
                    vep_id = col_var["id"]
            if vep_id:
                ids_mapping[vep_id] = hgvs_key
        var_data["vep_id"] = vep_id
        var_data["vep_id_data"] = None
        vep_data[hgvs_key] = var_data

    if ids_infile:
        ids_data = json.load(open(ids_infile))
    else:
        # Gather ids_list from colocated_variants in hgvs_data
        ids_data = vep_post(
            data_id="ids",
            data_list=list(ids_mapping.keys()),
            endpoint="variation/homo_sapiens",
            limit=200,
            outfile=ids_outfile,
        )

    for id_key in ids_data.keys():
        hgvs_key = ids_mapping[id_key]
        vep_data[hgvs_key]["vep_id_data"] = ids_data[id_key]
        vep_data[hgvs_key]["vep_id"] = id_key

    return vep_data


def vep_post(
    data_id: str,
    data_list: list,
    endpoint: str,
    server: str = "https://grch37.rest.ensembl.org/",
    headers: Optional[dict] = None,
    limit: int = 200,
    outfile: Optional[str] = None,
):
    """
    Wrapper to POST to the VEP API endpoints.

    Documentation:
       https://grch37.rest.ensembl.org/documentation/info/vep_region_post
       https://grch37.rest.ensembl.org/documentation/info/vep_id_post

    :param data_id: ID of data for post. ex: "hgvs_notations" or "ids"
    :param data_list: List of data strings in format required for data_id. ex: "1:g.1158631A>G" or "rs1234"
    :param endpoint: VEP endpoint. ex: "vep/human/hgvs" or "variation/homo_sapiens"
    :param server: ENSEMBL server. Default GRCH37 due to header of VCF containing /data/ref_genome/human_g1k_v37.fasta
    :param headers: Headers of API call. Default None and defined in function to avoid dict function definition
                    See https://stackoverflow.com/questions/26320899/why-is-the-empty-dictionary-a-dangerous-default-value-in-python
    :param limit: POST limit. Default 300 as it is the limit as per VEP HGVS documentation
    :param outfile: If defined, writes the response to a json outfile. Default does not write to file.
    :return: List or Dict of concatinated results
    """
    if headers is None:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
    results = None
    print(f"Starting VEP {endpoint} download of {len(data_list)} items")
    for i in range(0, len(data_list), limit):
        print(f"Downloading VEP info for items {i}-{i + limit - 1}")
        data_sub_list = data_list[i : i + limit]
        data_json = json.dumps({data_id: data_sub_list})
        sub_results = fetch_endpoint_post(server=server, request=endpoint, data=data_json, headers=headers)
        # Handles results returned as either dict or list
        if not results:
            if type(sub_results) == dict:
                results = {}
            elif type(sub_results) == list:
                results = []
        if type(sub_results) == dict:
            results = {**results, **sub_results}
        elif type(sub_results) == list:
            results += sub_results

    if outfile:
        with open(outfile, "w") as f:
            json.dump(results, f, indent=4)
    return results


def fetch_endpoint_post(server: str, request: str, data, headers: dict):
    """
    Generalized API post function call.

    Intended to be reusable for multiple POST API calls.

    Documentation:
        https://drive.google.com/file/d/1jm8DJOqHxiZCLL0gkMnuyhU3ulLzOUuD/view

    :param server: API server. ex: "https://grch37.rest.ensembl.org"
    :param request: Request (aka ext). ex: "/vep/human/hgvs"
    :param data: Post data. Can take many formats but usually dict.
    :param headers: Headers of API call. ex: {"Content-Type": "application/json", "Accept": "application/json"}
    :return: Dict or string of response.
    """
    response = requests.post(server + request, headers=headers, data=data)
    if response.status_code != HTTPStatus.OK:
        raise PostError(response.status_code, endpoint=server + request, headers=headers, data=data)
    if headers["Accept"] == "application/json":
        return response.json()
    else:
        return response.text
