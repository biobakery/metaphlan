#!/usr/bin/env python

__author__ = ('Duy Tin Truong (duytin.truong@unitn.it), '
              'Francesco Asnicar (f.asnicar@unitn.it), '
              'Moreno Zolfo (moreno.zolfo@unitn.it), '
              'Francesco Beghini (francesco.beghini@unitn.it), '
              'Aitor Blanco Miguez (aitor.blancomiguez@unitn.it)')
__version__ = '2.0.0'
__date__ = '17 Jul 2019'

import os, time, shutil, pickle
import subprocess as sb
import argparse as ap
from external_exec import execute, compose_command
from utils import error, info, optimized_dump
from cmseq import cmseq


"""
Global variables
"""
BREATH_THRESHOLD = 90


"""
Reads and parses the command line arguments of the script.

:returns: the parsed arguments
"""
def read_params():
    p = ap.ArgumentParser(description="")
    p.add_argument('-i', '--input', type=str, 
                   nargs='+', default=[],
                   help="The input samples as SAM or BAM files")
    p.add_argument('--sorted', action='store_true', default=False,
                   help="Whether the BAM input files are sorted [default=True]")
    p.add_argument('-f', '--input_format', type=str, default=None,
                   help="The input samples format [BAM, SAM, SAM/BAM.BZ2]")
    p.add_argument('-o', '--output_dir', type=str, default=None,
                   help="The output directory")
    p.add_argument('-n', '--nprocs', type=int, default=None,
                   help="The number of threads to execute the script")
    
    return p.parse_args()


"""
Checks the mandatory command line arguments of the script.

:returns: the checked args
"""
def check_params(args):
    if not args.input:
        error('-i (or --input) must be specified', exit=True, 
            init_new_line=True)
    elif not args.input_format:
        error('-f (or --input_format) must be specified', exit=True, 
            init_new_line=True)
    elif not args.output_dir:
        error('-o (or --output_dir) must be specified', exit=True, 
            init_new_line=True)
    elif args.input_format.lower() != "bam" and args.input_format.lower() != "sam" and args.input_format.lower() != "bz2":
        error('The input format must be SAM, BAM, or compressed in BZ2 format', 
            exit=True, init_new_line=True)
    else:
        check_input_files(args.input, args.input_format)
    if not args.output_dir.endswith('/'):
        args.output_dir += '/'
    if not args.nprocs:
        args.nprocs = 1
    
    return args


"""
Checks the input sample files

:param input: The input files
"""
def check_input_files(input, input_format):
    for s in input:
        _, extension = os.path.splitext(s)
        if not os.path.exists(s):
            error('The input file \"'+s+'\" does not exist', exit=True, 
                init_new_line=True)
        elif not input_format.lower() == extension[1:].lower():
            error('The the input file \"'+s+'\" must be in \"'+
                input_format.upper()+'\" format',
                exit=True, init_new_line=True)
    return True


#ToDo: Check CMSeq
"""
Checks the mandatory programs to execute of the script.

"""
def check_dependencies():
    try:
        # sb.check_call(["samtools", "tview"], stdout=sb.DEVNULL, stderr=sb.DEVNULL)
        sb.check_call(["bzip2", "--help"], stdout=sb.DEVNULL, stderr=sb.DEVNULL)
    except Exception as e:
        error('Program not installed or not present in the system path\n'+str(e), 
            init_new_line=True, exit=True)


"""
Converts SAM files to sorted BAM files using samtools

:param input: the list of samples as SAM files
:param tmp_dir: the temporal output directory
:returns: the list of sorted BAM files
"""
def sam_to_bam(input, tmp_dir, nprocs):
    bam = []
    params = {
        "program_name" : "samtools",
        "params" : "view",
        "input" : "-Sb",
        "command_line" : "#program_name# #params# #input# > #output#"
    }    
    #ToDo: parallelize
    for i in input:  
        n, _ = os.path.splitext(os.path.basename(i))      
        execute(compose_command(params, input_file=i, output_file=tmp_dir+n+".bam"))
        bam.append(tmp_dir+n+".bam")
    return sort_bam(bam, tmp_dir, nprocs)


"""
Sort BAM files using samtools

:param input: the list of samples as BAM files
:param tmp_dir: the temporal output directory
:returns: the list of sorted BAM files
"""
def sort_bam(input, tmp_dir, nprocs):
    sorted = []
    params = {
        "program_name" : "samtools",
        "params" : "sort",
        "command_line" : "#program_name# #params# #input# #output#"
    }
    #ToDo: parallelize
    for i in input:        
        n, _ = os.path.splitext(os.path.basename(i))        
        execute(compose_command(params, input_file=i, output_file=tmp_dir+n+".sorted"))
        sorted.append(tmp_dir+n+".sorted.bam")
    return sorted

    
"""
Decompressed BZ2 files

:param input: the list of samples as BZ2 files
:param tmp_dir: the temporal output directory
:returns: the list of decompressed files
"""
def decompress_bz2(input, tmp_dir, nprocs):
    decompressed = []
    decompressed_format = []
    params = {
        "program_name" : "bzip2",
        "input" : "-cdk",
        "command_line" : "#program_name# #input# > #output#"
    }
    #ToDo: parallelize
    for i in input:        
        f, _ = os.path.splitext(i)
        n, _ = os.path.splitext(os.path.basename(i))
        execute(compose_command(params, input_file=i, output_file=tmp_dir+n))
        _, e = os.path.splitext(f)
        decompressed.append(tmp_dir+n)
        decompressed_format.append(e)

    if decompressed_format[1:] == decompressed_format[:-1]:
        if decompressed_format[0][1:].lower() == "sam":
            return decompressed, "sam"
        elif decompressed_format[0][1:].lower() == "bam":
            return decompressed, "bam"
        else:
            error("Decompressed files are not in SAM or BAM format",
                exit=True, init_new_line=True)
    else:
        error("Decompressed files have different formats",
            exit=True, init_new_line=True)


"""
Convert input sample files to sorted BAMs

:param input: the samples as SAM or BAM files
:param sorted: whether the BAM files are sorted
:param input_format: format of the sample files [bam or sam]
:param tmp_dir: the temporal output directory
:param nprocs: number of threads to use in the execution
:returns: the new list of input BAM files
"""
def convert_inputs(input, sorted, input_format, tmp_dir, nprocs):
    if input_format.lower() == "bz2":
        info("Decompressing samples...\n", init_new_line=True)
        input, input_format = decompress_bz2(input, tmp_dir, nprocs)
        info("Done.")

    if input_format.lower() == "sam":
        info("Converting samples to BAM format...\n", init_new_line=True)
        input = sam_to_bam(input, tmp_dir, nprocs)
        info("Done.")
    elif sorted == False:        
        info("Sorting BAM samples...\n", init_new_line=True)
        input = sort_bam(input, tmp_dir, nprocs)
        info("Done.")
    
    return input


#ToDo: BREATH_THRESHOLD as command line parameter
"""
Gets the markers for each sample and writes the Pickle files

:param input: the samples as sorted BAM files
:param output_dir: the output directory
:param nprocs: number of threads to use in the execution
"""
def execute_cmseq(input, output_dir, nprocs):
    # Parallelize??    
    info("Getting consensus markers from samples...", init_new_line=True)
    for i in input:
        info("Processing sample: "+i, init_new_line=True)
        n, _ = os.path.splitext(os.path.basename(i))
        consensus = []
        collection = cmseq.BamFile(i, index=True, minlen=0)
        for c in collection.get_contigs():
            contig  = collection.get_contig_by_label(c)
            seq = contig.reference_free_consensus(noneCharacter='N')
            breath = get_breath(seq)
            if(breath >= BREATH_THRESHOLD):
                consensus.append({"marker":c, "breath":breath, "sequence":seq})
        
        markers_pkl = open(output_dir+n+'.pkl', 'wb')
        optimized_dump(markers_pkl, consensus)
    info("Done.", init_new_line=True)


"""
Gets the Breath of Coverage measure for a consensus sequence

:param sequence: the consensus sequence
:returns: the breath of coverage
"""
def get_breath(sequence):
    seq_len = len(sequence)
    return ((seq_len - sequence.count('N')) * 100) / seq_len    


"""
Gets the clade-specific markers from a list of aligned samples in 
SAM or BAM format and writes the results in Pickles files in the
user-selected output directory

:param input: the samples as SAM or BAM files
:param sorted: whether the BAM files are sorted
:param input_format: format of the sample files [bam or sam]
:param output_dir: the output directory
:param nprocs: number of threads to use in the execution
"""
def samples_to_markers(input, sorted, input_format, output_dir, nprocs):
    tmp_dir = output_dir+'tmp/'
    try:
        os.mkdir(tmp_dir, 755)
    except Exception as e:
        error('Folder \"'+tmp_dir+'\" already exists!\n'+str(e), exit=True,
            init_new_line=True)
    
    input = convert_inputs(input, sorted, input_format, tmp_dir, nprocs)
    execute_cmseq(input, output_dir, nprocs)        
    
    shutil.rmtree(tmp_dir, ignore_errors=False, onerror=None)


#Check samtools exit status 1
"""
Main function

:param input: the samples as SAM or BAM files
:param sorted: whether the BAM files are sorted
:param input_format: format of the sample files [bam or sam]
:param output_dir: the output directory
:param nprocs: number of threads to use in the execution
"""
if __name__ == "__main__":
    info("Start execution: "+format(time.ctime(int(time.time()))))
    args = read_params()
    check_dependencies()
    args = check_params(args)
    samples_to_markers(args.input, args.sorted, args.input_format, args.output_dir, args.nprocs)
    info("Finish execution: "+format(time.ctime(int(time.time())))+"\n", init_new_line=True)
