import { useEffect, useRef, useState } from "react";
const maxReconnectAttempts = 5;
let reconnectAttempts = 0;
export default function Proctoring() {
  const videoRef = useRef(null);
  const wsRef = useRef(null);
  const lastResultRef = useRef(null);
  const isProctoringRef = useRef(false);
  const [isProctoring, setIsProctoring] = useState(false);
  const [result, setResult] = useState({
    message: "",  // The toast message to display
    data: null,   // You can store any additional data here
  });
  const animationFrameId = useRef(null);

  const startProctoring = async () => {
    try {
      console.log("Requesting webcam access...");
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      console.log("Webcam access granted.");

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      console.log("Connecting to WebSocket...");
      wsRef.current = new WebSocket("ws://localhost:8000/ws/proctoring/");

      wsRef.current.onopen = () => {
        console.log("WebSocket connected");
        setIsProctoring(true);
        isProctoringRef.current = true;
        captureFrames();  // Start capturing frames
      };

      wsRef.current.onmessage = (event) => handleWebSocketMessage(event);

      wsRef.current.onclose = () => {
        console.log("WebSocket closed. Reconnecting...");
        if (lastResultRef.current) {
          console.log("Last object count:", lastResultRef.current.object_count);
        } else {
          console.log("No detection data received.");
        }
        if (reconnectAttempts < maxReconnectAttempts && isProctoringRef.current) {
          const delay = Math.random() * 5000; // Random delay between 0-5 sec
          setTimeout(startProctoring, delay);
          reconnectAttempts++;
        }
      };
      

      wsRef.current.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    } catch (error) {
      console.error("Error accessing webcam:", error);
    }
  };

  const stopProctoring = () => {
    console.log("Stopping proctoring...");
    
    if (animationFrameId.current) {
      cancelAnimationFrame(animationFrameId.current);
      animationFrameId.current = null;
    }

    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
    }

    if (wsRef.current) {
      console.log("Closing WebSocket...");
      wsRef.current.close();
      wsRef.current = null;
    }

    isProctoringRef.current = false;
    setIsProctoring(false);
  };

  const captureFrames = () => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
  
    const sendFrame = () => {
      if (!isProctoringRef.current || !videoRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        return;
      }
  
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  
      // Convert to grayscale
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      for (let i = 0; i < imageData.data.length; i += 4) {
        const gray = (imageData.data[i] + imageData.data[i + 1] + imageData.data[i + 2]) / 3;
        imageData.data[i] = gray;
        imageData.data[i + 1] = gray;
        imageData.data[i + 2] = gray;
      }
      ctx.putImageData(imageData, 0, 0);
  
      canvas.toBlob((blob) => {
        if (blob && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(blob);
        }
      }, "image/jpeg", 0.5);  // Lower JPEG quality for less bandwidth
  
      setTimeout(sendFrame, 300);  // Reduce frame rate dynamically
    };
  
    sendFrame();
  };
  
  

  const handleWebSocketMessage = (event) => {
    if (event.data instanceof Blob) {
      const imgURL = URL.createObjectURL(event.data);
      document.getElementById("videoFrame").src = imgURL;
    } else {
      const resultData = JSON.parse(event.data);
      setResult((prevResult) => {
        const newResult = {
          ...prevResult,
          message: resultData.message,
          cheating_detected: resultData.cheating_detected,
          object_count: resultData.object_count,
        };
        lastResultRef.current = newResult;  // Store last result
        return newResult;
      });
    }
  };

  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.key === "Enter") {
        stopProctoring();
      }
    };
    window.addEventListener("keydown", handleKeyPress);
    return () => {
      window.removeEventListener("keydown", handleKeyPress);
    };
  }, []);

  return (
    <div className="flex flex-col items-center p-4">
      <video id="videoFrame" ref={videoRef} autoPlay className="border rounded-lg shadow-lg" />
      {!isProctoring && (
        <button onClick={startProctoring} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg">
          Start Proctoring
        </button>
      )}
      {isProctoring && <p className="mt-4 text-red-500">Press ENTER to stop proctoring</p>}

      {result.message && (
        <div
          id="toast"
          style={{
            position: "fixed",
            bottom: "20px",
            left: "50%",
            transform: "translateX(-50%)",
            backgroundColor: "rgba(0,0,0,0.7)",
            color: "white",
            padding: "10px 20px",
            borderRadius: "5px",
            opacity: result.message ? "1" : "0",
            transition: "opacity 0.3s ease-in-out",
          }}
        >
          {result.message}
        </div>
      )}
    </div>
  );
}
