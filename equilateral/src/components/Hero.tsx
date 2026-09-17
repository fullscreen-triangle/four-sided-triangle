export function Hero() {
  return (
    <header className="hero">
      <div className="page">
        <div className="hero-kicker">Federated Retrieval-Augmentation</div>
        <h1 className="hero-title">
          Search as Individuation. Answers as Societies of Agents. Why a True Answer Can Be a Useless One.
        </h1>
        <p className="hero-sub">
          A retrieval-augmented system that returns a passage whose tokens match the query, drawn from a source that
          is true, can still be useless to the person who asked. This is not a ranking defect — it is a category
          error, forced by treating content as though it were meaning, and it is provable in finite weighted graphs.
        </p>
        <div className="hero-meta">
          <span>Kundai Farai Sachikonye</span>
          <span>AIMe Registry for Artificial Intelligence</span>
          <span>10 theorem groups · 10 validated experiments · every chart is a live simulation</span>
        </div>
        <div className="hero-cta">
          <a className="btn btn-primary" href="#floor">
            Start reading
          </a>
          <a className="btn" href="#toc">
            Jump to a section
          </a>
        </div>
      </div>
    </header>
  );
}
