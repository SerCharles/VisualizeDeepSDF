#Render the basic info of depth and norms of our ScanNet Dataset

base_source=/home/shenguanlin/dazuoye/results/Meshes/ShapeNetV2
base_target=/home/shenguanlin/result
base_code=/home/shenguanlin/VisualizeDeepSDF/src/render
cd $base_source

types=$(ls)
for type in $types
do 
    cd $base_target 
    mkdir $base_target/$type
    cd $base_source/$type 
    items=$(ls)
    for item in $items 
    do 
        cd $base_code
        python render.py --data_place=$base_source/$type/$item --save_place=$base_target/$type/$item
    done 
done