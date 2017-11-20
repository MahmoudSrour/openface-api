echo "Start Training..."

python /root/openface/util/align-dlib.py /src/training/images align outerEyesAndNose /src/training/aligned-images --size 96

/root/openface/batch-represent/main.lua -outDir /src/training/feature-images -data /src/training/aligned-images

python /root/openface/demos/classifier.py train /src/training/feature-images

echo "End Traing running app.py..."
echo "Start running app.py..."

python /src/app.py