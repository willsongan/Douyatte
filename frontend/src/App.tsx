import { useState } from "react";
import { IterationHub } from "./components/IterationHub";
import { NewFeatureIteration } from "./iterations/NewFeatureIteration";
import { WordContextIteration } from "./iterations/WordContextIteration";

type ActiveView = "hub" | "iteration-1" | "iteration-2";

function App() {
  const [view, setView] = useState<ActiveView>("hub");

  if (view === "iteration-1") {
    return <WordContextIteration onBack={() => setView("hub")} />;
  }

  if (view === "iteration-2") {
    return <NewFeatureIteration onBack={() => setView("hub")} />;
  }

  return (
    <IterationHub
      onSelectIteration1={() => setView("iteration-1")}
      onSelectIteration2={() => setView("iteration-2")}
    />
  );
}

export default App;
