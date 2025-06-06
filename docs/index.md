---
layout: default
title: Home
nav_order: 1
---

<div align="center">
  <h1>Four Sided Triangle</h1>
  <p><em>there is nothing new under the sun</em></p>
  <img src="four_sided_triangle.png" alt="Four-Sided Triangle Logo" width="300" style="margin: 20px 0;"/>
</div>

---

## Executive Summary

Four-Sided Triangle is a **sophisticated multi-model optimization pipeline** designed to overcome the limitations of traditional RAG (Retrieval-Augmented Generation) systems when dealing with complex domain-expert knowledge extraction. Unlike conventional approaches that rely on simple retrieval mechanisms, this system employs a novel **recursive optimization methodology** that treats language models as transformation functions within a complex optimization space.

The system's **metacognitive orchestration layer** manages an 8-stage specialized pipeline, dynamically selecting between LLM-based reasoning and traditional mathematical solvers based on problem characteristics. This hybrid approach allows the system to handle both fuzzy reasoning tasks and precise mathematical optimization problems with equal proficiency.

---

## 🚀 Why Four-Sided Triangle Is Necessary

Traditional AI approaches face several critical limitations when dealing with domain-expert knowledge:

<div class="feature-grid">
  <div class="feature-card">
    <h3>🧠 Knowledge Depth Problem</h3>
    <p>Standard RAG systems struggle with the depth and complexity of specialized knowledge domains, often providing superficial responses that fail to incorporate expert-level insights.</p>
  </div>
  
  <div class="feature-card">
    <h3>⚡ Optimization Complexity</h3>
    <p>Real-world problems often require sophisticated multi-objective optimization that standard LLMs cannot perform effectively without specialized architectural support.</p>
  </div>
  
  <div class="feature-card">
    <h3>🔄 Context Management Challenge</h3>
    <p>Managing context across complex reasoning chains overwhelms conventional architectures, leading to context fragmentation and reasoning failures.</p>
  </div>
  
  <div class="feature-card">
    <h3>✅ Quality Consistency Issues</h3>
    <p>Ensuring consistent quality in outputs across diverse problem spaces requires sophisticated monitoring and evaluation protocols absent in simple pipeline approaches.</p>
  </div>
</div>

Four-Sided Triangle addresses these challenges through its specialized architecture, providing a comprehensive solution for complex knowledge extraction and reasoning tasks.

---

## 🏗️ System Architecture Overview

### Metacognitive Orchestrator: The Central Intelligence

The **metacognitive orchestrator** provides the essential adaptive intelligence layer that coordinates all system components and dynamically adjusts processing strategies based on the nature of each query.

**Key Components:**
- **Working Memory System**: Maintains state and context throughout query processing
- **Process Monitor**: Continuously evaluates output quality across all stages  
- **Dynamic Prompt Generator**: Enables sophisticated model interactions

### Advanced Core Components

#### 🧬 Glycolytic Query Investment Cycle (GQIC)
Optimizes resource allocation based on expected information yield using a metabolic-inspired approach with three phases: Initiation, Investment, and Payoff.

#### 🔍 Metacognitive Task Partitioning (MTP)
Breaks complex queries into optimally sized sub-tasks using self-interrogative principles with knowledge domain identification and dependency modeling.

#### 🛡️ Adversarial Throttle Detection and Bypass (ATDB)
Detects and overcomes throttling mechanisms in LLMs that limit their capabilities, ensuring consistent high-quality responses.

---

## 🔄 Eight-Stage Specialized Pipeline

<div class="pipeline-stages">
  <div class="stage-row">
    <div class="stage">
      <strong>Stage 0</strong><br>
      <a href="stages/query-processing">Query Processor</a><br>
      <small>Transforms ambiguous natural language queries</small>
    </div>
    <div class="stage">
      <strong>Stage 1</strong><br>
      <a href="stages/semantic-atdb">Semantic ATDB</a><br>
      <small>Performs semantic transformation and throttle detection</small>
    </div>
    <div class="stage">
      <strong>Stage 2</strong><br>
      <a href="stages/domain-knowledge">Domain Knowledge</a><br>
      <small>Extracts and organizes domain-specific knowledge</small>
    </div>
    <div class="stage">
      <strong>Stage 3</strong><br>
      <a href="stages/reasoning-optimization">Parallel Reasoning</a><br>
      <small>Applies mathematical and logical reasoning</small>
    </div>
  </div>
  
  <div class="stage-row">
    <div class="stage">
      <strong>Stage 4</strong><br>
      <a href="stages/solution-generation">Solution Generation</a><br>
      <small>Produces candidate solutions from reasoning outputs</small>
    </div>
    <div class="stage">
      <strong>Stage 5</strong><br>
      <a href="stages/response-scoring">Response Scoring</a><br>
      <small>Evaluates candidates using quality metrics</small>
    </div>
    <div class="stage">
      <strong>Stage 6</strong><br>
      <a href="stages/response-comparison">Ensemble Diversification</a><br>
      <small>Creates diverse set of high-quality solutions</small>
    </div>
    <div class="stage">
      <strong>Stage 7</strong><br>
      <a href="stages/threshold-verification">Threshold Verification</a><br>
      <small>Performs final verification against quality standards</small>
    </div>
  </div>
</div>

---

## 🤖 Specialized Models

The system integrates multiple specialized models across different stages:

| Stage | Primary Models | Purpose |
|-------|---------------|---------|
| **Query Processing** | Phi-3-mini, Mixtral, SciBERT | Structured output, complex transformations, NER |
| **Domain Knowledge** | BioMedLM, Mixtral, Phi-3-mini | Biomechanics, sports statistics, lightweight fallback |
| **Reasoning** | Qwen, DeepSeek Math, Phi-3-mini | Mathematical reasoning, equation solving, fast CoT |
| **Quality Assessment** | OpenAssistant Reward Model | Human preference evaluation |
| **Diversity Scoring** | BGE Reranker M3 | Pairwise diversity and quality scoring |

---

## 🚀 Getting Started

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/four-sided-triangle.git
cd four-sided-triangle

# Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run with Docker
docker-compose up -d

# Access the API
curl http://localhost:8000/health
```

### Prerequisites

- **Python 3.10+**
- **Docker and Docker Compose** (for containerized deployment)
- **CUDA-capable GPU** (recommended but not required)
- **32GB RAM minimum** for optimal performance

---

## 📚 Documentation

<div class="docs-grid">
  <div class="docs-section">
    <h3>📖 Core Documentation</h3>
    <ul>
      <li><a href="getting-started">Getting Started Guide</a></li>
      <li><a href="architecture">System Architecture</a></li>
      <li><a href="pipeline">Pipeline Architecture</a></li>
      <li><a href="api-reference">API Reference</a></li>
    </ul>
  </div>
  
  <div class="docs-section">
    <h3>🔧 Development</h3>
    <ul>
      <li><a href="contributing">Contributing Guidelines</a></li>
      <li><a href="frontend-development">Frontend Development</a></li>
      <li><a href="adr/">Architecture Decisions</a></li>
      <li><a href="models">Model Documentation</a></li>
    </ul>
  </div>
  
  <div class="docs-section">
    <h3>⚙️ Components</h3>
    <ul>
      <li><a href="core-processing">Core Processing</a></li>
      <li><a href="model-container">Model Container</a></li>
      <li><a href="interpreter">Interpreter Component</a></li>
      <li><a href="data-models">Data Models</a></li>
    </ul>
  </div>
  
  <div class="docs-section">
    <h3>🎨 Frontend</h3>
    <ul>
      <li><a href="frontend-overview">Frontend Overview</a></li>
      <li><a href="frontend-components">Components</a></li>
      <li><a href="frontend-development">Development Guide</a></li>
      <li><a href="tasks">Tasks API</a></li>
    </ul>
  </div>
</div>

---

## 🏆 Key Features

- **🧠 Metacognitive Orchestration**: Central orchestration layer managing the entire pipeline
- **🔧 Modular Architecture**: Each component is independent and can be modified or replaced
- **⚡ Advanced Optimization**: Sophisticated optimization techniques at multiple levels
- **✅ Quality Assurance**: Comprehensive quality checks and verification at each stage
- **🎯 Ensemble Diversification**: Novel approach to response generation and combination
- **📊 Bayesian Evaluation**: Rigorous quality assessment using Bayesian frameworks
- **🔄 Hybrid Optimization**: Combines LLM-based reasoning with traditional mathematical solvers
- **📈 Scalable Deployment**: Supports local, Docker, Kubernetes, and cloud deployments

---

## 📊 Performance

The system is designed for:

- **📈 Scalability**: Handles increasing workloads efficiently with distributed computing support
- **🛡️ Reliability**: Robust error handling and recovery mechanisms
- **🎯 Quality**: Comprehensive quality assurance across all pipeline stages
- **⚡ Speed**: Optimized for performance with GPU acceleration and parallel processing

---

## 🤝 Support & Community

- **🐛 Issues**: Use the [GitHub issue tracker](https://github.com/your-org/four-sided-triangle/issues)
- **💬 Discussions**: Join our [GitHub Discussions](https://github.com/your-org/four-sided-triangle/discussions)
- **📖 Documentation**: Browse this comprehensive documentation
- **🔧 Contributing**: See our [Contributing Guidelines](contributing)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/your-org/four-sided-triangle/blob/main/LICENSE) file for details.

---

<div class="acknowledgments">
  <h2>🙏 Acknowledgments</h2>
  <p>Special thanks to:</p>
  <ul>
    <li>The open-source community for foundational tools and libraries</li>
    <li>Our contributors and maintainers for continuous improvement</li>
    <li>The research teams behind the integrated specialized models</li>
    <li>The academic community for advancing the field of AI and optimization</li>
  </ul>
</div>

<style>
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.feature-card {
  background: #f6f8fa;
  border: 1px solid #d1d9e0;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.pipeline-stages {
  margin: 20px 0;
}

.stage-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin: 15px 0;
}

.stage {
  background: #e1f5fe;
  border: 2px solid #0277bd;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  transition: transform 0.2s;
}

.stage:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.docs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.docs-section {
  background: #f8f9fa;
  border-left: 4px solid #28a745;
  padding: 20px;
  border-radius: 0 8px 8px 0;
}

.acknowledgments {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 20px;
  margin: 30px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

table th, table td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}

table th {
  background-color: #f2f2f2;
  font-weight: bold;
}
</style> 