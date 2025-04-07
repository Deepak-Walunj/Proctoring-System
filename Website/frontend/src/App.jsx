import VideoAnalysis from "./VideoAnalysis";
import { useState } from "react";

export default function App() {
  const [vivaStarted, setVivaStarted] = useState(false);

  const vivaHandler = () => {
    setVivaStarted((prev) => !prev);
    console.log(vivaStarted ? "Viva ended" : "Viva started");
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
      <VideoAnalysis endviva={vivaStarted} username="test_user" vivaID="12345" />
    </div>
  );
}
