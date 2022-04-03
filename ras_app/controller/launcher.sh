#!/bin/bash

#python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat < ~/out.all.8.txt
#git add /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat
#git commit -m "New mat"
#git push

for i in 493 153 296 478 156 280 447 159 340 426 182 255 389
do 
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 8 > ~/out.$i.8.txt
	python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat < ~/out.$i.8.txt
done 

for i in 570 153 343 523 227 312 466 278 443 463 297 306 450
do 
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 10 > ~/out.$i.10.txt
	python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat < ~/out.$i.10.txt
done

for i in 124 31 67 122 32 66 113 43 83 108 48 56 106
do 
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 2 > ~/out.$i.2.txt
	python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat < ~/out.$i.2.txt
done

for i in 240 67 170 210 100 147 198 102 176 192 119 138 188
do 
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 4 > ~/out.$i.4.txt
	python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat < ~/out.$i.4.txt
done