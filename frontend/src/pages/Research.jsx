function Research() {
  return (
    <div className="command-page">
      <section className="command-hero">
        <div>
          <p className="eyebrow">QUANT RESEARCH TERMINAL</p>
          <h1>Research Lab</h1>
          <p className="hero-subtitle">
            Test strategies, validate signals, analyze news impact, and prepare trade ideas before execution.
          </p>
        </div>
      </section>

      <section className="research-grid">
        <div className="research-card">
          <p className="eyebrow">STRATEGY TESTING</p>
          <h2>Strategy Lab</h2>
          <p>
            Backtest SMA, RSI, stop-loss, and risk rules against individual stocks.
          </p>
          <button>Open Strategy Lab</button>
        </div>

        <div className="research-card">
          <p className="eyebrow">MARKET DISCOVERY</p>
          <h2>Market Screener</h2>
          <p>
            Scan your watchlist and rank stocks by confidence, risk, trend, and backtest strength.
          </p>
          <button>Open Screener</button>
        </div>

        <div className="research-card">
          <p className="eyebrow">NEWS INTELLIGENCE</p>
          <h2>News Impact</h2>
          <p>
            Analyze market-moving news, event type, sentiment, source quality, and trade relevance.
          </p>
          <button>Open News Intelligence</button>
        </div>

        <div className="research-card">
          <p className="eyebrow">AI ANALYST</p>
          <h2>Research Notes</h2>
          <p>
            Generate bull case, bear case, technical view, risk view, and trade thesis for any ticker.
          </p>
          <button>Open AI Research</button>
        </div>
      </section>
    </div>
  );
}

export default Research;