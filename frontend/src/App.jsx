import React, { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [verified, setVerified] = useState(false);

  const [loading, setLoading] = useState(false);
  const [extractedText, setExtractedText] = useState("");
  const [documentInfo, setDocumentInfo] = useState(null);
  const [error, setError] = useState("");

  const [searchQuery, setSearchQuery] = useState("");
  const [researchResults, setResearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);

  const [totalDocuments, setTotalDocuments] = useState(0);
  const [totalClaims, setTotalClaims] = useState(0);
  const [verifiedClaims, setVerifiedClaims] = useState(0);

  // STEP 8: AI CLAIM EXTRACTION STATES
  const [claims, setClaims] = useState([]);
  const [claimLoading, setClaimLoading] = useState(false);

  // DOCUMENT EXTRACTION
  const handleVerify = async () => {
    if (!file) return;

    setLoading(true);
    setError("");
    setVerified(false);
    setExtractedText("");
    setDocumentInfo(null);
    setClaims([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "https://citeverify-3qoo.onrender.com",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Document processing failed.");
      }

      setExtractedText(data.extracted_text);
      setDocumentInfo({
        filename: data.filename,
        fileType: data.file_type,
        pageCount: data.page_count,
        wordCount: data.word_count,
      });
      setVerified(true);
      setTotalDocuments((prev)=>prev+1)
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ACADEMIC RESEARCH SEARCH
  const handleResearchSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearchLoading(true);
    setError("");

    try {
      const response = await fetch(
        `https://citeverify-3qoo.onrender.com${encodeURIComponent(
          searchQuery
        )}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Research search failed.");
      }

      const combined = [...data.results.crossref, ...data.results.openalex];
      setResearchResults(combined);
    } catch (err) {
      setError(err.message);
    } finally {
      setSearchLoading(false);
    }
  };

  // STEP 8: AI SCIENTIFIC CLAIM EXTRACTION
  const handleClaimExtraction = async () => {
    if (!file) return;

    setClaimLoading(true);
    setError("");
    setClaims([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "https://citeverify-3qoo.onrender.com",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Claim extraction failed.");
      }

      const extractedClaims=data.claims||[];
      setClaims(extractedClaims);
      setTotalClaims((prev)=>prev+extractedClaims.length)
    } catch (err) {
      setError(err.message);
    } finally {
      setClaimLoading(false);
    }
  };

  // FILE VALIDATION
  const handleFile = (selectedFile) => {
    if (!selectedFile) return;

    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];

    if (
      !allowedTypes.includes(selectedFile.type) &&
      !selectedFile.name.toLowerCase().endsWith(".docx") &&
      !selectedFile.name.toLowerCase().endsWith(".pdf")
    ) {
      alert("Please upload a PDF or DOCX file.");
      return;
    }

    setFile(selectedFile);
    setVerified(false);
    setExtractedText("");
    setDocumentInfo(null);
    setClaims([]);
    setError("");
  };

  // DRAG AND DROP
  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  return (
    <div className="app">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">CV</div>
          <div>
            <h2>CiteVerify</h2>
            <span>RESEARCH INTELLIGENCE</span>
          </div>
        </div>

        <div className="menu-title">WORKSPACE</div>

        <nav>
          <div className="nav-item active">▦ Dashboard</div>
          <div className="nav-item">▤ Documents</div>
          <div className="nav-item">⌕ Verification History</div>
          <div className="nav-item">▧ Reports</div>
        </nav>

        <div className="sidebar-bottom">
          <div className="status-dot"></div>
          System Ready
          <p>AI Research Assistant</p>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main">
        <header className="topbar">
          <div>
            <h3>Research Dashboard</h3>
            <p>Scientific Claim & Citation Verification</p>
          </div>

          <div className="profile">
            <div className="avatar">R</div>
            <span>Researcher</span>
          </div>
        </header>

        <section className="welcome">
          <div>
            <span className="eyebrow">ACADEMIC INTEGRITY PLATFORM</span>
            <h1>
              Welcome to <span>CiteVerify.</span>
            </h1>
            <p>
              Verify scientific claims. Validate research citations. Build
              trustworthy academic documents.
            </p>
          </div>

          <div className="welcome-symbol">CV</div>
        </section>

        {/* STATISTICS */}
        <section className="stats">
          <div className="stat-card">
            <span>Total Documents</span>
            <h2>--</h2>
            <small>Documents uploaded</small>
          </div>

          <div className="stat-card">
            <span>Claims Detected</span>
            <h2>{claims.length || "--"}</h2>
            <small>Scientific statements</small>
          </div>

          <div className="stat-card">
            <span>Citations Found</span>
            <h2>--</h2>
            <small>References identified</small>
          </div>

          <div className="stat-card">
            <span>Verified Claims</span>
            <h2>--</h2>
            <small>Evidence assessment pending</small>
          </div>
        </section>

        {/* UPLOAD SECTION */}
        <section className="content-grid">
          <div className="upload-card">
            <div className="section-heading">
              <div>
                <h2>Upload Research Document</h2>
                <p>Start a new scientific verification process.</p>
              </div>
              <span className="upload-icon">↑</span>
            </div>

            {/* DROPZONE */}
            <div
              className={`dropzone ${dragging ? "dragging" : ""}`}
              onDragOver={(e) => {
                e.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
            >
              <div className="file-icon">PDF</div>
              <h3>Drag and drop your document</h3>
              <p>or browse files from your computer</p>

              <label className="browse-btn">
                Browse Files
                <input
                  type="file"
                  accept=".pdf,.docx"
                  hidden
                  onChange={(e) => handleFile(e.target.files[0])}
                />
              </label>

              <small>Supported formats: PDF, DOCX</small>
            </div>

            {/* SELECTED FILE */}
            {file && (
              <div className="selected-file">
                <div className="file-icon small">DOC</div>
                <div className="file-details">
                  <strong>{file.name}</strong>
                  <span>{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                </div>

                <button
                  className="remove-btn"
                  onClick={() => {
                    setFile(null);
                    setVerified(false);
                    setExtractedText("");
                    setDocumentInfo(null);
                    setClaims([]);
                    setError("");
                  }}
                >
                  ✕
                </button>
              </div>
            )}

            {/* DOCUMENT EXTRACTION BUTTON */}
            <button
              className="verify-btn"
              disabled={!file || loading || claimLoading}
              onClick={handleVerify}
            >
              {loading ? "Processing Document..." : "Start Verification →"}
            </button>

            {/* AI CLAIM EXTRACTION BUTTON */}
            <button
              className="verify-btn"
              disabled={!file || claimLoading || loading}
              onClick={handleClaimExtraction}
            >
              {claimLoading
                ? "AI Analyzing..."
                : "Extract Scientific Claims →"}
            </button>

            {/* ERROR */}
            {error && <div className="error-message">{error}</div>}

            {/* ACADEMIC RESEARCH DISCOVERY */}
            <div className="claims-section">
              <h2>Academic Research Discovery</h2>
              <p>Search original scientific publications.</p>

              <input
                type="text"
                placeholder="Enter research topic or paper title..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="research-input"
              />

              <button
                className="verify-btn"
                onClick={handleResearchSearch}
                disabled={searchLoading}
              >
                {searchLoading ? "Searching..." : "Search Research Papers"}
              </button>

              {researchResults.map((paper, index) => (
                <div className="claim-card" key={`${paper.source}-${index}`}>
                  <h3>{paper.title}</h3>

                  <p>
                    <strong>Authors:</strong>{" "}
                    {paper.authors?.join(", ") || "Not available"}
                  </p>

                  <p>
                    <strong>Year:</strong> {paper.year || "Not available"}
                  </p>

                  <p>
                    <strong>DOI:</strong> {paper.doi || "Not available"}
                  </p>

                  <p>
                    <strong>Database:</strong> {paper.source}
                  </p>

                  {paper.url && (
                    <a href={paper.url} target="_blank" rel="noreferrer">
                      View Research Paper →
                    </a>
                  )}
                </div>
              ))}
            </div>

            {/* DOCUMENT EXTRACTION RESULT */}
            {documentInfo && (
              <div className="extraction-result">
                <h3>Document Processed Successfully ✓</h3>

                <div className="document-stats">
                  <div>
                    <strong>{documentInfo.pageCount || "N/A"}</strong>
                    <span>Pages</span>
                  </div>

                  <div>
                    <strong>{documentInfo.wordCount}</strong>
                    <span>Words Extracted</span>
                  </div>

                  <div>
                    <strong>{documentInfo.fileType.toUpperCase()}</strong>
                    <span>File Type</span>
                  </div>
                </div>

                <h4>Extracted Document Text</h4>
                <div className="extracted-text">{extractedText}</div>
              </div>
            )}

            {/* STEP 8: AI-DETECTED CLAIMS */}
            {claims.length > 0 && (
              <div className="claims-section">
                <h2>AI-Detected Scientific Claims</h2>
                <p>Total claims identified: {claims.length}</p>

                {claims.map((claim) => (
                  <div className="claim-card" key={claim.claim_id}>
                    <span>CLAIM #{claim.claim_id}</span>
                    <h3>{claim.original_claim}</h3>

                    <p>
                      <strong>Category:</strong> {claim.category}
                    </p>

                    <p>
                      <strong>Citation:</strong>{" "}
                      {claim.citation || "No citation detected"}
                    </p>

                    <p>
                      <strong>Explanation:</strong> {claim.simplified_claim}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* WORKFLOW */}
          <div className="workflow-card">
            <h2>How CiteVerify Works</h2>
            <p className="workflow-subtitle">
              A transparent research verification pipeline.
            </p>

            <div className="workflow-step">
              <div className="step-number">01</div>
              <div>
                <h4>Document Analysis</h4>
                <p>Extract scientific claims and citations.</p>
              </div>
            </div>

            <div className="workflow-step">
              <div className="step-number">02</div>
              <div>
                <h4>Source Retrieval</h4>
                <p>Locate original academic publications.</p>
              </div>
            </div>

            <div className="workflow-step">
              <div className="step-number">03</div>
              <div>
                <h4>Evidence Comparison</h4>
                <p>Compare claims against research findings.</p>
              </div>
            </div>

            <div className="workflow-step">
              <div className="step-number">04</div>
              <div>
                <h4>Verification Report</h4>
                <p>Generate verdicts with evidence and links.</p>
              </div>
            </div>
          </div>
        </section>

        {/* VERIFICATION STATUS */}
        <section className="results-card">
          <div className="section-heading">
            <div>
              <h2>Verification Overview</h2>
              <p>Claim classification results will appear here.</p>
            </div>
            <span className="pending-label">AWAITING DOCUMENT</span>
          </div>

          <div className="result-grid">
            <div className="result-item">
              <div className="result-dot green"></div>
              <div>
                <h3>Supported</h3>
                <p>Evidence confirms the claim.</p>
              </div>
            </div>

            <div className="result-item">
              <div className="result-dot yellow"></div>
              <div>
                <h3>Partially Supported</h3>
                <p>Evidence supports some aspects.</p>
              </div>
            </div>

            <div className="result-item">
              <div className="result-dot red"></div>
              <div>
                <h3>Unsupported</h3>
                <p>Evidence does not establish the claim.</p>
              </div>
            </div>

            <div className="result-item">
              <div className="result-dot orange"></div>
              <div>
                <h3>Contradictory</h3>
                <p>Evidence conflicts with the claim.</p>
              </div>
            </div>
          </div>
        </section>

        <footer>
          CiteVerify © 2026 | Built for Academic Trust & Integrity
        </footer>
      </main>
    </div>
  );
}

export default App;
