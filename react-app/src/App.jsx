import { useState } from 'react';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>🏭 Industrial IoT Predictive Maintenance</h1>
        <p>Edge AI • Federated Learning • Blockchain Security • Digital Twin</p>
      </header>
      <Dashboard />
    </div>
  );
}

export default App;
