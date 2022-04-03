#!/bin/bash

#python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat < ~/out.all.8.txt
#git add /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat
#git commit -m "New mat"
#git push

for i in 365 147 272 338 158 221 331 173 281 329 198 217 290
do 
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 10 > ~/out.$i.10.txt
	python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat < ~/out.$i.10.txt
done

for i in 289 119 167 268 143 163 262 154 168 231 159 161 197
do 
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 8 > ~/out.$i.8.txt
	python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat < ~/out.$i.8.txt
done 

for i in 143 58 87 128 65 77 99 71 115 94 74 75 92
do 
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 4 > ~/out.$i.4.txt
	python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat < ~/out.$i.4.txt
done

for i in 72 29 48 71 34 47 65 35 49 60 40 45 50
do 
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 2 > ~/out.$i.2.txt
	python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat < ~/out.$i.2.txt
done