#!/bin/bash
#$ -S /bin/bash
#$ -l h_vmem=50G -l s_vmem=50G
#$ -N Hazard_7
#$ -cwd
#$ -V
#$ -o Logs/output_single.txt
#$ -e Logs/error_single.txt

~/anaconda3/bin/python main.py data/TheGoodPlace.graphml -d 09/19/2016 -m 7 --trend > Logs/main_Output_single.log 2> Logs/main_Error_single.log
## $SGE_TASK_ID <- will repeat from 1 to 6.
