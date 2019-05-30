#!/bin/bash
mkdir -p output
python2 ../strainphlan.py --mpa_pkl ../metaphlan_databases/mpa_v29_CHOCOPhlAn_201901.pkl \
                         --ifn_samples consensus_markers/*.markers \
                         --ifn_markers db_markers/s__Bacteroides_caccae.markers.fasta \
                         --ifn_ref_genomes reference_genomes/G000273725.fna \
                         --output_dir output \
                         --nprocs_main 10 \
                         --clades s__Bacteroides_caccae | tee output/log.txt

python2 ../strainphlan_src/add_metadata_tree.py \
        --ifn_trees output/RAxML_bestTree.s__Bacteroides_caccae.tree \
        --ifn_metadatas fastqs/metadata.txt \
        --metadatas subjectID
