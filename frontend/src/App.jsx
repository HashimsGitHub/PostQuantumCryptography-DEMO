import React, { useState } from "react";

const scenarios = [
  {
    id: "classical-rsa",
    title: "Conventional RSA + AES",
    label: "CLASSICAL MODE",
    risk: "Future quantum risk",
    stages: ["RSA key pair", "AES session key", "Encrypt payload", "Wrap AES key", "Bob decrypts"],
    terminal: [
      "Initialising classical RSA scenario...",
      "Generating RSA-2048 key pair...",
      "RSA public/private keys created.",
      "Generating AES-256 session key...",
      "Encrypting message using AES-GCM...",
      "Wrapping AES key using RSA-OAEP...",
      "Sending encrypted payload...",
      "Bob decrypting AES key...",
      "Bob decrypting message...",
      "SUCCESS: classical process completed."
    ],
    teaching: [
      "AES encrypts the actual data.",
      "RSA protects the AES key.",
      "Future quantum computers threaten RSA, not AES-256 itself."
    ]
  },
  {
    id: "weak-rsa-break",
    title: "Weak RSA Break",
    label: "ATTACK SIMULATION",
    risk: "Factoring attack principle",
    stages: ["Weak RSA key", "Encrypt value", "Factor n", "Recover private key", "Decrypt"],
    terminal: [
      "Loading weak RSA example...",
      "Publishing toy RSA public key...",
      "Encrypting demo value...",
      "Eve intercepts ciphertext...",
      "Factoring modulus n...",
      "Recovering p and q...",
      "Calculating private exponent d...",
      "Decrypting ciphertext...",
      "SUCCESS: weak RSA break demonstrated."
    ],
    teaching: [
      "This uses deliberately tiny RSA values.",
      "Factoring n exposes the private key.",
      "This demonstrates the principle, not a real RSA-2048 break."
    ]
  },
  {
    id: "harvest-now",
    title: "Harvest Now, Decrypt Later",
    label: "ENTERPRISE RISK",
    risk: "Captured today, decrypted later",
    stages: ["Capture traffic", "Store ciphertext", "Wait years", "Quantum capability", "Future exposure"],
    terminal: [
      "Capturing encrypted traffic...",
      "Saving public key and ciphertext...",
      "Archiving packet record...",
      "Waiting for future compute capability...",
      "Quantum capability assumed available...",
      "Attempting historical decryption...",
      "RISK: long-lived encrypted data may be exposed later."
    ],
    teaching: [
      "Attackers may store encrypted traffic today.",
      "Sensitive data can still matter years later.",
      "PQC migration reduces future decryption risk."
    ]
  },
  {
    id: "pqc-mlkem",
    title: "Post-Quantum ML-KEM + AES",
    label: "PQC MODE",
    risk: "Quantum-resistant key establishment",
    stages: ["ML-KEM key pair", "Encapsulate secret", "Decapsulate secret", "Derive AES key", "Bob decrypts"],
    terminal: [
      "Initialising ML-KEM scenario...",
      "Generating ML-KEM key pair...",
      "Publishing Bob's ML-KEM public key...",
      "Alice encapsulates shared secret...",
      "Bob decapsulates KEM ciphertext...",
      "Shared secrets match.",
      "Deriving AES-256 key from shared secret...",
      "Encrypting and decrypting payload...",
      "SUCCESS: PQC key establishment completed."
    ],
    teaching: [
      "ML-KEM establishes the shared secret.",
      "AES still encrypts the data.",
      "The RSA factoring attack path is removed."
    ]
  }
];

function JsonBlock({ data }) {
  return <pre className="json-block">{JSON.stringify(data, null, 2)}</pre>;
}

export default function App() {
  const [selected, setSelected] = useState(scenarios[3]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stageIndex, setStageIndex] = useState(-1);
  const [terminal, setTerminal] = useState([
    "> System ready.",
    "> Select scenario and run process."
  ]);

  function resetScenario(scenario) {
    setSelected(scenario);
    setResult(null);
    setStageIndex(-1);
    setTerminal([
      "> Scenario loaded: " + scenario.title,
      "> Awaiting RUN PROCESS."
    ]);
  }

  function writeTerminal(line) {
    setTerminal((prev) => [...prev, "> " + line]);
  }

  async function runProcess() {
    setLoading(true);
    setResult(null);
    setStageIndex(0);
    setTerminal([]);

    const terminalSteps = selected.terminal;
    const maxStage = selected.stages.length - 1;

    let current = 0;

    const timer = setInterval(() => {
      if (terminalSteps[current]) {
        writeTerminal(terminalSteps[current]);
      }

      const calculatedStage = Math.min(
        Math.floor((current / Math.max(terminalSteps.length - 1, 1)) * maxStage),
        maxStage
      );

      setStageIndex(calculatedStage);
      current += 1;

      if (current >= terminalSteps.length) {
        clearInterval(timer);
      }
    }, 650);

    try {
      const response = await fetch(`/api/scenario/${selected.id}`);
      const data = await response.json();

      setTimeout(() => {
        setResult(data);
        setStageIndex(maxStage);
        setLoading(false);
        writeTerminal("Backend response received.");
        writeTerminal("Execution time: " + (data.time_ms || "N/A") + " ms.");
        writeTerminal("Live cryptographic result available.");
      }, terminalSteps.length * 650 + 200);
    } catch (error) {
      setResult({
        status: "error",
        title: "Scenario failed",
        summary: error.message,
        crypto: {
          troubleshooting: [
            "docker logs pqc-demo-backend",
            "docker logs pqc-demo-frontend",
            "curl http://localhost/api/health"
          ]
        }
      });
      setLoading(false);
      writeTerminal("ERROR: " + error.message);
    }
  }

  return (
    <div className="matrix-page">
      <div className="matrix-rain"></div>

      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">▣</div>
          <div>
            <h1>POST QUANTUM</h1>
            <h2>CRYPTOGRAPHY DEMO</h2>
            <p>/// Developed by </p><p>HASHIM HILAL</p>
          </div>
        </div>

        <nav className="scenario-nav">
          {scenarios.map((scenario) => (
            <button
              key={scenario.id}
              className={`nav-item ${selected.id === scenario.id ? "active" : ""}`}
              onClick={() => resetScenario(scenario)}
            >
              <span>›_</span>
              <div>
                <strong>{scenario.title}</strong>
                <small>{scenario.label}</small>
              </div>
            </button>
          ))}
        </nav>

        <div className="key-message">
          <span>KEY MESSAGE</span>
          <p>
            PQC changes how keys are established. AES still encrypts the data.
          </p>
        </div>

        <div className="terminal-window">
          <div className="terminal-title">TERMINAL VIEW</div>
          <div className="terminal-body">
            {terminal.map((line, index) => (
              <div key={`${line}-${index}`}>{line}</div>
            ))}
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="header">
          <div>
            <span className="terminal-label">SCENARIO</span>
            <h1>{selected.title}</h1>
            <p>{selected.label} // {selected.risk}</p>
          </div>

          <button className="run" disabled={loading} onClick={runProcess}>
            {loading ? "PROCESS RUNNING" : "▷ RUN PROCESS"}
          </button>
        </header>

        <section className="actors">
          <div className="entity">
            <div className="entity-icon">A</div>
            <h3>ALICE</h3>
            <p>Sender</p>
            <small>Creates secure payload</small>
          </div>

          <div className="link active-link">······························</div>

          <div className="entity">
            <div className="entity-icon">B</div>
            <h3>BOB</h3>
            <p>Receiver</p>
            <small>Decrypts using valid key material</small>
          </div>

          <div className="link active-link">······························</div>

          <div className="entity attacker">
            <div className="entity-icon">E</div>
            <h3>EVE</h3>
            <p>Observer</p>
            <small>Captures traffic and attempts analysis</small>
          </div>

          <div className="link">······························</div>

          <div className="entity quantum">
            <div className="entity-icon">Q</div>
            <h3>QUANTUM</h3>
            <p>Future capability</p>
            <small>Threat model for public-key crypto</small>
          </div>
        </section>

        <section className="process">
          <div className="section-title">PROCESS FLOW</div>
          <div className="stage-grid">
            {selected.stages.map((stage, index) => (
              <div
                key={stage}
                className={`stage ${
                  index < stageIndex ? "done" : index === stageIndex ? "current" : ""
                }`}
              >
                <div className="stage-number">{index + 1}</div>
                <p>{stage}</p>
              </div>
            ))}
          </div>

          <div className="progress-track">
            <div
              className="progress-fill"
              style={{
                width:
                  stageIndex < 0
                    ? "0%"
                    : `${((stageIndex + 1) / selected.stages.length) * 100}%`
              }}
            ></div>
          </div>

          <div className="process-status">
            STEP {stageIndex < 0 ? 0 : stageIndex + 1} OF {selected.stages.length}
          </div>
        </section>

        <section className="bottom-grid">
          <div className="panel">
            <div className="section-title">TEACHING POINT</div>
            <ul className="teaching-list">
              {selected.teaching.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            {result?.teaching_point && (
              <div className="teaching-output">{result.teaching_point}</div>
            )}
          </div>

          <div className="panel">
            <div className="section-title">LIVE RESULT</div>
            {!result && !loading && <div className="empty">Awaiting execution...</div>}
            {loading && <div className="running">Executing cryptographic operation on backend...</div>}
            {result && (
              <div className="summary">
                <p><strong>Status:</strong> {result.status}</p>
                <p><strong>Time:</strong> {result.time_ms || "N/A"} ms</p>
                <p><strong>Summary:</strong> {result.summary || result.title}</p>
              </div>
            )}
          </div>

          <div className="panel crypto">
            <div className="section-title">CRYPTO DETAILS</div>
            {result ? (
              <JsonBlock data={result.crypto || result} />
            ) : (
              <div className="empty">JSON output will appear here.</div>
            )}
          </div>
        </section>

        <footer className="footer">
          <span>[SYSTEM READY]</span>
          <span>LIVE BACKEND DEMO</span>
          <span>RSA // AES // ML-KEM</span>
        </footer>
      </main>
    </div>
  );
}