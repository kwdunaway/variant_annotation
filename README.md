# Variant Annotation Prototype

## Purpose

Prototype a variant annotation tool. 

Each variant is annotated in a tsv file with the following pieces of information:

1. Depth of sequence coverage at the site of variation.
2. Number of reads supporting the variant.
3. Percentage of reads supporting the variant versus those supporting reference reads.
4. Gene of the variant, 
5. Type of variation (substitution, insertion, CNV, etc.) 
6. Variation effect (missense, silent, intergenic, etc.).
7. The minor allele frequency of the variant if available.

See `data/expected_outfile.tsv` for an example of the expected output from this codebase.
 
## Installation

This repo utilizes pysam (htslib python wrapper) to process VCFs. As such, installing [samtools](http://www.htslib.org/download/) is a prerequisite 

After samtools is installed, it is advised to use a virtual environment like virtualenv. Then run the following for an editable install:
```
pip install -e .
```

Confirm everything installed correctly by running pytests:
```
pytest tests
```

## Running

To annotate variants, use the inputting a VCF and specifying output path. An example would be:
```
python var_annot/bin.py data/test_vcf_data.txt data/outfile.tsv
```

Read `var_annot/bin.py` to understand the optional parameters. A quick test is to run:
```
python var_annot/bin.py data/test_vcf_data.txt data/outfile.tsv --hgvs_infile=data/hgvs.json --ids_infile=data/ids.json 
diff data/outfile.tsv data/expected_outfile.tsv
```

## Additional Context

The overall functionality of this code is to:

1. Load the VCF in the Variants class utilizing pysam.
2. Get the annotations via API calls to the VEP endpoints: vep/human/hgvs and variation/homo_sapiens
3. Fill out the Variant information with the VEP annotation data.
4. Write the annotated variant information to a TSV file.

Some interesting callouts:

* There are a couple of good VCF parsing tools out there. This utilizes pysam. If you want to use a different parser, you would need to make small adjustments at the Variants.load_vcf() and Variant() functions.
* This utilizes the GRCH37 VEP endpoints due to the header of the example VCF containing "/data/ref_genome/human_g1k_v37.fasta"
* If you want to utilize a different reference genome, it would only require a couple of simple tweeks to vep_post() and get_vep_data(). This would include changing the endpoint and limit variables.
* This utilizes POST endpoints instead of GET to limit the runtime connectivity requirements to just two steps. It may be a bit harder to intuit but doing it this way is a lifesaver if your API calls fail.
* In order to get the variant type, this calls the variation/homo_sapiens endpoint utilizing variant ids (primarily rsids). There are other ways to determine variant type but if that changes the logic for MAF also needs to change.
* This is a small enough code base it could all go in one file. But for readability and scalability the functionality is separated into 4 files: bin, variants, ensembl, and exception.
* Testing is light, future directions include adding more test coverage and edge cases
