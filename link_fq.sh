wenku_list="DES01011 DES01013"
for wenku in $wenku_list;
do
    for fastq in `ls /TJPROJ1/DENOVO/PROJECT/libenping/ruanjianjie/yancao_hanyue/01.QC/yancao_0927/${wenku}*/01.Duplication/*clean.rd.fq.gz`;
    do                                                                                                                                
        ln -s $fastq fastq/
    done
done                                                                                                                  

wenku_list="DES01009"
for wenku in $wenku_list;
do
    for fastq in `ls /TJPROJ1/DENOVO/PROJECT/libenping/ruanjianjie/yancao_hanyue/01.QC/${wenku}*/01.Duplication/*clean.rd.fq.gz`;
    do
        ln -s $fastq fastq/
    done
done
