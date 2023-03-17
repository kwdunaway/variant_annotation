#!/usr/bin/env python
"""
Data classes defining Variants with added functionality for manipulating them.
"""

from typing import Optional
from pysam import VariantFile
from pysam.libcbcf import VariantRecord
from var_annot.ensembl import get_vep_data


class Variants:
    """Data class managing many Variant classes as well as functions to manipulate them."""

    def __init__(self, infile_path: str):
        """
        Initializes the Variants from a VCF data file.

        :param infile_path: Path to VCF input file
        :return: None
        """
        self.data = {}
        self.variants_order = []
        self.load_vcf(infile_path=infile_path)

    def load_vcf(self, infile_path: str):
        """
        Loads VCF data from file.

        :param infile_path: Path to VCF input file
        :return: None
        """
        vcf_in = VariantFile(infile_path)  # auto-detect input format
        for record in vcf_in.fetch():
            # Process multiple alt alleles for sample
            for alt_index in range(len(record.alts)):
                var = Variant(record=record, alt_index=alt_index)
                self.data[var.vep_hgvs] = var
                self.variants_order.append(var.vep_hgvs)

    def add_vep_info(
        self,
        hgvs_infile: Optional[str] = None,
        hgvs_outfile: Optional[str] = None,
        ids_infile: Optional[str] = None,
        ids_outfile: Optional[str] = None,
    ):
        """
        Adds VEP information to the Variants.

        Calls VEP APIs to obtain the information. If infiles are provided this function
        will load the data from the infiles. If outfiles are provided it will save the
        data to outfile paths.

        :param hgvs_infile: Loads HGVS data from this JSON file.
        :param hgvs_outfile: Writes HGVS data to this JSON file path.
        :param ids_infile: Loads Variant ID data from this JSON file.
        :param ids_outfile: Writes Variant ID data to this JSON file path.
        :return: None
        """
        vep_data = get_vep_data(
            hgvs_list=list(self.data.keys()),
            hgvs_infile=hgvs_infile,
            hgvs_outfile=hgvs_outfile,
            ids_infile=ids_infile,
            ids_outfile=ids_outfile,
        )
        for vep_key in vep_data.keys():
            self.data[vep_key].vep_content = vep_data[vep_key]

            # Processes the gene name data
            genes = set()
            self.data[vep_key].variant_effect = vep_data[vep_key]["most_severe_consequence"]
            if "transcript_consequences" in vep_data[vep_key]:
                for tc in vep_data[vep_key]["transcript_consequences"]:
                    ignored_genes = [
                        "Clone_based_vega_gene",
                        "Clone_based_ensembl_gene",
                        "Uniprot_gn",
                    ]
                    if (
                        self.data[vep_key].variant_effect in tc["consequence_terms"]
                        and tc["gene_symbol_source"] not in ignored_genes
                    ):
                        genes.add(tc["gene_symbol_source"])
                self.data[vep_key].gene_name = ",".join(genes)

            # Processes the id, variant_type, and MAF data
            if vep_data[vep_key]["vep_id_data"]:
                self.data[vep_key].vep_id = vep_data[vep_key]["vep_id"]
                self.data[vep_key].variant_type = vep_data[vep_key]["vep_id_data"]["var_class"]
                self.data[vep_key].maf = vep_data[vep_key]["vep_id_data"]["MAF"]

    def write(self, out_file: str):
        """
        Writes relevant data to output TSV file.

        :param out_file: Path to output file.
        :return: None
        """
        header_list = [
            "chrom",
            "pos",
            "id",
            "ref",
            "alt",
            "total_depth",
            "variant_depth",
            "variant_percentage",
            "gene",
            "variation_type",
            "variation_effect",
            "MAF",
        ]
        with open(out_file, "w") as out_fh:
            out_line = "\t".join(header_list) + "\n"
            out_fh.write(out_line)
            for vep_hgvs in self.variants_order:
                var = self.data[vep_hgvs]
                variant_id = "."
                if var.vep_id:
                    variant_id = var.vep_id
                line_list = [
                    var.chrom,
                    var.pos,
                    variant_id,
                    var.ref,
                    var.alt,
                    var.depth,
                    var.var_depth,
                    var.var_percentage,
                    var.gene_name,
                    var.variant_type,
                    var.variant_effect,
                    var.maf,
                ]
                # clean up output list
                clean_line_list = []
                for item in line_list:
                    if item:
                        clean_line_list.append(str(item))
                    else:
                        clean_line_list.append("N/A")
                out_line = "\t".join(clean_line_list) + "\n"
                out_fh.write(out_line)


class Variant:
    """Data class containing relelant information at the Variant level."""

    def __init__(self, record: VariantRecord, alt_index=0):
        self.chrom = record.contig
        self.pos = record.pos
        self.ref = record.ref
        self.alt = record.alts[alt_index]
        self.vep_hgvs = f"{self.chrom}:g.{self.pos}{self.ref}>{self.alt}"  # ex: "1:g.1158631A>G"
        self.depth = record.samples[0]["NR"][alt_index]  # total depth
        self.var_depth = record.samples[0]["NV"][alt_index]  # Variant depth
        # Percentage of reads supporting the variant versus those supporting reference reads.
        self.var_percentage = 100 * (self.var_depth / self.depth)
        # Values defined by VEP HGVS annotation. Initialized to None until VEP is queried.
        self.vep_id = None
        self.vep_content = None
        self.gene_name = None
        self.variant_type = None
        self.variant_effect = None
        self.maf = None  # The minor allele frequency of the variant if available.
        # Any additional annotations that you feel might be relevant.
        self.record = record  # vcf record, not printed to outfile but could easily be if you want.
