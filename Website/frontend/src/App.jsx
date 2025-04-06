import { useEffect, useRef, useState } from "react";

const maxReconnectAttempts = 5;
let reconnectAttempts = 0;

export default function Proctoring() {
  const videoRef = useRef(null);
  const wsRef = useRef(null);
  const wsFaceRef = useRef(null);
  const lastResultRef = useRef(null);
  const isProctoringRef = useRef(false);
  const [isProctoring, setIsProctoring] = useState(false);
  const canvasRef = useRef(document.createElement("canvas"));
  const frameIntervalRef = useRef(null);
  const [objectResult, setObjectResult] = useState({
    message: "",  // The toast message to display
    data: null,   // You can store any additional data here
  });
  const [faceResult, setFaceResult] = useState({
    message: "",  // The toast message to display
    data: null,   // You can store any additional data here
  });
  const animationFrameId = useRef(null);
  const FRAME_RATE = 300; // Frame rate in ms (100ms = 10fps)

  const startProctoring = async () => {
    try {
        console.log("Requesting webcam access...");
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        console.log("Webcam access granted.");
        if (videoRef.current) {
            videoRef.current.srcObject = stream;
        }
        console.log("Creating WebSockets...");

        const createWebSocket = (url, type, wsRef) => {
            wsRef.current = new WebSocket(url);
            wsRef.current.onopen = () => {
                console.log(`${type} WebSocket connected`);
                reconnectAttempts = 0; // ✅ Reset reconnect attempts
                setIsProctoring(true);
                if (type === "Object Detection") {
                    isProctoringRef.current = true;
                }
                setTimeout(() => captureFrames(wsRef.current, videoRef, canvasRef), 100);
            };
            wsRef.current.onmessage = (event) => {
                type === "Object Detection" ? handleWebSocketMessageObject(event) : handleWebSocketMessageFace(event);
            };
            wsRef.current.onclose = () => {
                console.log(`${type} WebSocket closed.`);
                handleWebSocketClose(type)();
            };
            wsRef.current.onerror = (error) => {
                console.error(`${type} WebSocket Error:`, error);
                if (typeof handleWebSocketError === "function") {
                    handleWebSocketError(type)(error);
                } else {
                    console.warn("handleWebSocketError is not defined.");
                }
            };
        };
        // Create Object Detection WebSocket immediately
        createWebSocket("ws://localhost:8000/ws/object-detection/", "Object Detection", wsRef);
        // Create Face Detection WebSocket after a short delay to avoid race conditions
        setTimeout(() => {
            createWebSocket("ws://localhost:8000/ws/face-detection/", "Face Detection", wsFaceRef);
        });
    } catch (error) {
        console.error("Error accessing webcam:", error);
    }
};

  const captureFrames = (ws, videoRef, canvasRef) => {
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
    }
    const sendFrame = () => {
      if (!isProctoringRef.current || !videoRef.current || ws.readyState !== WebSocket.OPEN) return;
      
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");
      
      if (video.videoWidth > 0 && video.videoHeight > 0) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  
        canvas.toBlob((blob) => {
          if (blob && ws.readyState === WebSocket.OPEN) {
            ws.send(blob);
          }
        }, "image/jpeg", 0.5);
      }
    };
  
    frameIntervalRef.current = setInterval(sendFrame, FRAME_RATE);
  };
  
  const stopProctoring = () => {
    console.log("Stopping proctoring...");
    isProctoringRef.current = false;
  
    if (animationFrameId.current) {
      cancelAnimationFrame(animationFrameId.current);
      animationFrameId.current = null;
    }
  
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
    }
  
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  
    if (wsFaceRef.current) {
      wsFaceRef.current.close();
      wsFaceRef.current = null;
    }
  
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }
  
    setIsProctoring(false);
  };
  
  const handleWebSocketMessageObject = (event) => {
    if (event.data instanceof Blob) {
      const imgURL = URL.createObjectURL(event.data);
      document.getElementById("videoFrame").src = imgURL;
    } else {
      const resultData = JSON.parse(event.data);
      console.log("Received Object WebSocket Data:", resultData);
      setObjectResult((prevResult) => {
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

  const handleWebSocketMessageFace = (event) => {
    if (event.data instanceof Blob) {
      const imgURL = URL.createObjectURL(event.data);
      document.getElementById("videoFrame").src = imgURL;
    } else {
      const resultData1 = JSON.parse(event.data);
      console.log("Received Face WebSocket Data:", resultData1);
      setFaceResult((prevResult) => {
        const newResult1 = {
          ...prevResult,
          fDetection_toast: resultData1.fDetection_toast,
          mDetection_toast: resultData1.mDetection_toast,
        };
        lastResultRef.current = newResult1;  // Store last result
        return newResult1;
      });
    }
  };

  const handleWebSocketClose = (type) => () => {
    console.log(`${type} WebSocket closed.`);
    reconnectWebSocket(type);
  };

  const reconnectWebSocket = (type) => {
    if (reconnectAttempts >= maxReconnectAttempts || !isProctoringRef.current) {
      console.log(`Max reconnect attempts reached for ${type}.`);
      return;
    }
    const delay = Math.random() * 5000;
    console.log(`${type} WebSocket reconnecting in ${delay.toFixed(2)}ms...`);
    setTimeout(() => {
      reconnectAttempts++;
      if (type === "Object Detection") {
        wsRef.current = new WebSocket("ws://localhost:8000/ws/object-detection/");
        wsRef.current.onopen = () => console.log("Reconnected to Object Detection WebSocket");
        wsRef.current.onmessage = handleWebSocketMessageObject;
        wsRef.current.onclose = () => handleWebSocketClose("Object Detection");
        wsRef.current.onerror = (error) => handleWebSocketError("Object Detection")(error);
      } else if (type === "Face Detection") {
        wsFaceRef.current = new WebSocket("ws://localhost:8000/ws/face-detection/");
        wsFaceRef.current.onopen = () => console.log("Reconnected to Face Detection WebSocket");
        wsFaceRef.current.onmessage = handleWebSocketMessageFace;
        wsFaceRef.current.onclose = () => handleWebSocketClose("Face Detection");
        wsFaceRef.current.onerror = (error) => handleWebSocketError("Face Detection")(error);
      }
    }, delay);
  };

  const handleWebSocketError = (type) => (error) => {
    console.error(`${type} WebSocket error:`, error);
    if (reconnectAttempts >= maxReconnectAttempts || !isProctoringRef.current) {
      console.log(`Max reconnect attempts reached for ${type}.`);
      return;
    }
    
    reconnectAttempts++;
    setTimeout(() => reconnectWebSocket(type), Math.random() * 5000);
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

      {/* Toast for general message */}
      {objectResult.message && (
        <div
          id="message-toast"
          style={{
            position: "fixed",
            bottom: "20px",
            left: "50%",
            transform: "translateX(-50%)",
            backgroundColor: "rgba(0,0,0,0.7)",
            color: "white",
            padding: "10px 20px",
            borderRadius: "5px",
            opacity: objectResult.message ? "1" : "0",
            transition: "opacity 0.3s ease-in-out",
          }}
        >
          {objectResult.message}
        </div>
      )}

      {/* Toast for face detection */}
      {faceResult.fDetection_toast && (
        <div
          id="face-detection-toast"
          style={{
            position: "fixed",
            bottom: "80px",  // Adjust position for separation
            left: "50%",
            transform: "translateX(-50%)",
            backgroundColor: "rgba(255, 0, 0, 0.8)", // Red background for face detection
            color: "white",
            padding: "10px 20px",
            borderRadius: "5px",
            opacity: faceResult.fDetection_toast ? "1" : "0",
            transition: "opacity 0.3s ease-in-out",
          }}
        >
          {faceResult.fDetection_toast}
        </div>
      )}

      {/* Toast for object detection */}
      {faceResult.mDetection_toast && (
        <div
          id="object-detection-toast"
          style={{
            position: "fixed",
            bottom: "140px",  // Adjust position for separation
            left: "50%",
            transform: "translateX(-50%)",
            backgroundColor: "rgba(0, 0, 255, 0.8)", // Blue background for object detection
            color: "white",
            padding: "10px 20px",
            borderRadius: "5px",
            opacity: faceResult.mDetection_toast ? "1" : "0",
            transition: "opacity 0.3s ease-in-out",
          }}
        >
          {faceResult.mDetection_toast}
        </div>
      )}
    </div>
  );
  };
  
