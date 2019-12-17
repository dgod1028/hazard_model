#!/bin/bash
#$ -S /bin/bash
#$ -l h_vmem=50G -l s_vmem=50G
#$ -N Hazard_Model
#$ -cwd
#$ -V
#$ -t 1-9
#$ -o Logs/output.txt
#$ -e Logs/error.txt

~/anaconda3/bin/python main2.py data/ThisIsUs.graphml -d 09/19/2016 -m $SGE_TASK_ID --trend > Logs/Tmain_Output_$SGE_TASK_ID.log 2> Logs/Tmain_Error_$SGE_TASK_ID.log
## $SGE_TASK_ID <- will repeat from 1 to 6.
