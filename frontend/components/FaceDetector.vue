<template>
    <div class="video-container">
      <video ref="videoElement" autoplay muted width="630" height="490"></video>
      <canvas ref="canvasElement"></canvas>
    </div>
</template>
  
<script setup>
import * as faceapi from 'face-api.js';
const emit = defineEmits(); 
const videoElement = ref(null);  // Reference for the video element
const canvasElement = ref(null); // Reference for the canvas element
const detections = ref(null);    // Reactive ref for face detections
let videoStream = null;           // Store the video stream
let detectionInterval = null;     // Store the interval ID
let canvas = null

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
}})

// Load Face API models
const loadModels = async () => {
    const MODEL_URL = '/models'; // Local model directory
    await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL);
    await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
    await faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL);
    await faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL);

    startVideo();
};
  
// Start video stream from webcam
const startVideo = () => {
    navigator.mediaDevices.getUserMedia({ video: {} })
        .then(stream => {
        videoElement.value.srcObject = stream;
        videoStream = stream;
        })
        .catch(err => console.error("Error starting video: ", err));
};

  // Detect faces in real-time
const detectFaces = async () => {
    const options = new faceapi.TinyFaceDetectorOptions();
    canvas = canvasElement.value;
    const video = videoElement.value;

    faceapi.matchDimensions(canvas, video);

    // Detect faces at intervals
    detectionInterval = setInterval(async () => {
        detections.value = await faceapi.detectSingleFace(video, options)
        .withFaceLandmarks()

        const resizedDetections = faceapi.resizeResults(detections.value, video);
        canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
        if(detections.value){
            faceapi.draw.drawDetections(canvas, resizedDetections);
        }

    }, 100);
};

const allowPhotoTaking = ref(false)
  
// Watch for changes in detections
watch(detections, (newDetections) => {
    if(!detections){
        canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
    }

    if (newDetections) {
        allowPhotoTaking.value = true
        emit('face-detected', true)
    } else {
        allowPhotoTaking.value = false
        emit('face-detected', false)
    }
});


const capturePhoto = async () => {
  const video = videoElement.value;
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');

  const options = new faceapi.TinyFaceDetectorOptions();
  const detection = await faceapi.detectSingleFace(video, options).withFaceLandmarks();

  if (!detection) {
    console.warn("No face detected at capture.");
    return;
  }

  const { box } = detection.detection;

  // Set canvas size to match the bounding box size
  canvas.width = box.width;
  canvas.height = box.height;

  // Draw only the face region
  context.drawImage(
    video,
    box.x, box.y, box.width, box.height,  // Source
    0, 0, box.width, box.height           // Destination
  );

  // Convert canvas to Blob
  canvas.toBlob((blob) => {
    const photoURL = URL.createObjectURL(blob);
    emit('photo-taken', photoURL); // Send cropped face
  }, 'image/png');
};

  
// Expose the `capturePhoto` method to the parent
defineExpose({
  capturePhoto
});
  
// Automatically load models and start detecting faces when the component is mounted
onMounted(() => {
    loadModels();
    detectFaces();
});

// Cleanup resources when the component is unmounted
onUnmounted(() => {
  if (detectionInterval) {
    clearInterval(detectionInterval); // Clear the detection interval
  }
  if (videoStream) {
    videoStream.getTracks().forEach(track => track.stop()); // Stop all video tracks
  }
});

watch(() => props.isOpen, (newValue) => {
  if(newValue == false){
    if (detectionInterval) {
        clearInterval(detectionInterval); // Clear the detection interval
    }
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop()); // Stop all video tracks
    }
  }
})
</script>
  
<style scoped>
  .video-container {
    position: relative;
    width: 630px;
    height: 490px;
  }
  
  video {
    width: 100%;
    height: 100%;
  }
  
  canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none; /* Prevent interactions with the canvas */
  }
  </style>
  