#!/usr/bin/env python
"""
Entry point to interact with code via command line.
"""
import argparse
import logging

from var_annot.variants import Variants

log = logging.getLogger(__file__)


def pars_args() -> argparse.Namespace:
    """"""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_vcf", type=str, help="Path to input VCF file")
    parser.add_argument("output_tsv", type=str, help="Path to output TSV file")
    parser.add_argument("--hgvs_infile", type=str, help="Path to hgvs input json file", default=None)
    parser.add_argument(
        "--hgvs_outfile",
        type=str,
        help="Saves hgvs download to this path",
        default=None,
    )
    parser.add_argument("--ids_infile", type=str, help="Path to ids input json file", default=None)
    parser.add_argument("--ids_outfile", type=str, help="Saves ids download to this path", default=None)
    return parser.parse_args()


def main(args: argparse.Namespace):
    """"""
    variants = Variants(infile_path=args.input_vcf)
    variants.add_vep_info(
        hgvs_infile=args.hgvs_infile,
        hgvs_outfile=args.hgvs_outfile,
        ids_infile=args.ids_infile,
        ids_outfile=args.ids_outfile,
    )
    variants.write(out_file=args.output_tsv)


if __name__ == "__main__":
    main(pars_args())
