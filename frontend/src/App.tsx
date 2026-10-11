import { Routes, Route } from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import { Home } from "./pages/Home";
import { Copilot } from "./pages/Copilot";
import { Conflicts } from "./pages/Conflicts";
import { GraphExplorer } from "./pages/GraphExplorer";
import { Documents } from "./pages/Documents";
import { ExpertCapture } from "./pages/ExpertCapture";
import { Benchmarks } from "./pages/Benchmarks";
import { Dashboard } from "./pages/Dashboard";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/copilot" element={<Copilot />} />
        <Route path="/conflicts" element={<Conflicts />} />
        <Route path="/graph" element={<GraphExplorer />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/expert" element={<ExpertCapture />} />
        <Route path="/benchmarks" element={<Benchmarks />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Route>
    </Routes>
  );
}

export default App;
