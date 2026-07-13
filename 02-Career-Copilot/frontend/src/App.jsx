import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function ResultList({ title, items }) {
  if (!items?.length) {
    return null;
  }

  return (
    <section className="result-card">
      <h3>{title}</h3>

      <ul>
        {items.map((item, index) => (
          <li key={`${title}-${index}`}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

function App() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setResult(null);

    if (!resume) {
      setError("Please select a resume PDF.");
      return;
    }

    if (jobDescription.trim().length < 20) {
      setError("Please enter a longer job description.");
      return;
    }

    const formData = new FormData();
    formData.append("file", resume);
    formData.append("job_description", jobDescription);

    try {
      setIsAnalyzing(true);

      const response = await fetch(`${API_URL}/analyze-resume`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to analyze the resume.");
      }

      setResult(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsAnalyzing(false);
    }
  }

  const analysis = result?.analysis;

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">AI-powered job application assistant</p>
        <h1>Career Copilot</h1>
        <p>
          Upload your resume and paste a job description to receive an
          evidence-based fit analysis, recommendations, and interview questions.
        </p>
      </section>

      <section className="workspace">
        <form className="analysis-form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="resume">Resume PDF</label>

            <input
              id="resume"
              type="file"
              accept="application/pdf"
              onChange={(event) => {
                setResume(event.target.files?.[0] || null);
              }}
            />

            {resume && <small>Selected: {resume.name}</small>}
          </div>

          <div className="field">
            <label htmlFor="job-description">Job description</label>

            <textarea
              id="job-description"
              rows="14"
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder="Paste the complete job description here..."
            />
          </div>

          <button type="submit" disabled={isAnalyzing}>
            {isAnalyzing ? "Analyzing..." : "Analyze Resume"}
          </button>

          {error && <p className="error-message">{error}</p>}
        </form>

        <section className="results-panel">
          {!result && !isAnalyzing && (
            <div className="empty-state">
              <h2>Your analysis will appear here</h2>
              <p>
                Career Copilot will compare your resume with the job description.
              </p>
            </div>
          )}

          {isAnalyzing && (
            <div className="empty-state">
              <h2>Analyzing your application...</h2>
              <p>This may take a few seconds.</p>
            </div>
          )}

          {result && analysis && (
            <div className="results">
              <div className="result-header">
                <div>
                  <p className="eyebrow">Analysis complete</p>
                  <h2>{result.filename}</h2>
                  <p>{result.pages} PDF page(s) processed</p>
                </div>

                <span className={`fit-badge fit-${analysis.fit_level}`}>
                  {analysis.fit_level} fit
                </span>
              </div>

              <section className="result-card">
                <h3>Overall fit</h3>
                <p>{analysis.overall_fit}</p>
              </section>

              <section className="result-card">
                <h3>Matched qualifications</h3>

                <div className="evidence-list">
                  {analysis.matched_qualifications.map((item, index) => (
                    <article key={`match-${index}`} className="evidence-item">
                      <strong>{item.qualification}</strong>
                      <p>{item.evidence}</p>
                    </article>
                  ))}
                </div>
              </section>

              <section className="result-card">
                <h3>Qualification gaps</h3>

                {analysis.missing_qualifications.length === 0 ? (
                  <p>No major qualification gaps were identified.</p>
                ) : (
                  <div className="evidence-list">
                    {analysis.missing_qualifications.map((item, index) => (
                      <article key={`gap-${index}`} className="evidence-item">
                        <strong>{item.qualification}</strong>
                        <p>{item.reason}</p>
                      </article>
                    ))}
                  </div>
                )}
              </section>

              <ResultList
                title="Recommendations"
                items={analysis.recommendations}
              />

              <ResultList
                title="Likely interview questions"
                items={analysis.interview_questions}
              />
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

export default App;