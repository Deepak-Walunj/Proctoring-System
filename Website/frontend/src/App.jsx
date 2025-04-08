import VideoAnalysis from "./VideoAnalysis";
import { useState } from "react";

export default function App() {
  const [vivaStarted, setVivaStarted] = useState(false);

  const vivaHandler = () => {
    setVivaStarted((prev) => {
      const newState = !prev;
      console.log(newState ? "Viva started" : "Viva ended");
      return newState;
    });
    console.log("Viva Ending..."); 
    setVivaStarted(false); 
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Video Analysis App</h1>
      </header>
      <button
          className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
          onClick={vivaHandler}
        >
          Start Viva
        </button>
      <VideoAnalysis endviva={vivaStarted} username="Deepak Walunj" vivaID="12345" vivaHandler={vivaHandler}  />
    </div>
  );
}
