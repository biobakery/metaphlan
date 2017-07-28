# MetaPhlAn2 example


from qiime2.plugin import Plugin, Int
from q2_types.sample_data import SampleData
from q2_types.per_sample_sequences import SequencesWithQuality, PairedEndSequencesWithQuality
from q2_types.feature_table import FeatureTable, Frequency
from . import _metaphlan2


plugin = Plugin(
    name='metaphlan2',
    version='2.6.1',
    website='http://segatalab.cibio.unitn.it/tools/metaphlan2/',
    user_support_text='metaphlan-users@googlegroups.com',
    package='metaphlan2',
    citation_text=('Truong DT, Franzosa EA, Tickle TL, Scholz M, Weingart G, Pasolli E, Tett A, Huttenhower C, Segata N. MetaPhlAn2 for enhanced metagenomic taxonomic profiling. Nature Methods. 2015 Oct 1;12(10):902-3'),
    description=('MetaPhlAn is a computational tool for profiling the composition of microbial communities (Bacteria, Archaea, Eukaryotes, and Viruses) from metagenomic shotgun sequencing data with species level resolution'),
    short_description='MetaPhlAn2 for enhanced metagenomic taxonomic profiling'
)

plugin.methods.register_function(
    function=_metaphlan2.metaphlan2_single_fastq,

    inputs={'raw_data': SampleData[SequencesWithQuality] },
    input_descriptions={'raw_data': ('metagenomic shotgun sequencing data')},

    parameters={'nproc': Int},
    parameter_descriptions={'nproc': 'The number of CPUs to use for parallelizing the mapping, default 1 (no parallelization)'},

    outputs=[('tsv_table', FeatureTable[Frequency])],
    output_descriptions={'tsv_table': 'TAB-separated text file containing relative abundances of the species found in the input'},

    name='MetaPhlAn2 taxonomic profiling',
    description=('MetaPhlAn is a computational tool for profiling the composition of microbial communities (Bacteria, Archaea, Eukaryotes, and Viruses) from metagenomic shotgun sequencing data with species level resolution')
)

plugin.methods.register_function(
    function=_metaphlan2.metaphlan2_paired_fastq,

    inputs={'raw_data': SampleData[PairedEndSequencesWithQuality] },
    input_descriptions={'raw_data': ('metagenomic shotgun sequencing data')},

    parameters={'nproc': Int},
    parameter_descriptions={'nproc': 'The number of CPUs to use for parallelizing the mapping, default 1 (no parallelization)'},

    outputs=[('tsv_table', FeatureTable[Frequency])],
    output_descriptions={'tsv_table': 'TAB-separated text file containing relative abundances of the species found in the input'},

    name='MetaPhlAn2 taxonomic profiling',
    description=('MetaPhlAn is a computational tool for profiling the composition of microbial communities (Bacteria, Archaea, Eukaryotes, and Viruses) from metagenomic shotgun sequencing data with species level resolution')
)
