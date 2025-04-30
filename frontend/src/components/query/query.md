# RAG System Functional Architecture

## LLM Integration Architecture

The system uses three primary LLM integrations:

1. **Primary General LLM** (e.g., OpenAI GPT-4, Claude 3)
    - Handles general reasoning, query understanding, and response formulation
    - Accessed via REST API calls to provider endpoints
    - Capable of structured JSON output and natural language processing

2. **Domain-Specific LLM** (e.g., specialized sprint science model)
    - Provides domain expertise for mathematical models and scientific principles
    - Accessed through a dedicated API endpoint
    - Specialized in formulas, parameter relationships, and domain constraints

3. **Tool-Augmented LLM** (e.g., function-calling enabled model)
    - Handles specific structured tasks like entity extraction and relationship mapping
    - Used for converting natural language to structured representations
    - Specialized in categorization, classification, and structure formation

## Cross-Component Data Flow

The system passes increasingly refined data structures between components:

1. **Query → Modeler**: Raw user input is transformed into query intent, context, and metadata.

2. **Modeler → Solver**: Unstructured query becomes a structured entity-relationship model with domain-specific parameters.

3. **Solver → Interpreter**: The structured model with reasoning becomes a comprehensive solution package with supporting evidence.

## Component Functional Descriptions

### 1. Query Component

#### Query Processing Functions
- **Query Reception**: Captures user's natural language input through frontend interface
- **Query Preprocessing**: Standardizes text by removing noise, correcting spelling, normalizing terminology
- **Intent Classification**: Determines whether the query is informational, computational, or comparative
- **Context Incorporation**: Enriches query with user history, preferences, domain context
- **Query Validation**: Verifies query meets minimum information requirements for processing
- **Query Packaging**: Prepares standardized package for transfer to modeling component

#### Data Flow Description
- **Input**: Raw user text from UI input field
- **Processing**: Uses primary LLM to analyze text structure and intent
- **Output**: Structured query object with intent classification and metadata

#### LLM Interaction
- The component sends the raw query to the primary LLM with a system prompt specifying intent detection
- The LLM responds with query classification and structured interpretation
- Multiple query interpretations may be generated and compared for confidence

### 2. Modeler Component

#### Conceptual Modeling Functions
- **Entity Extraction**: Identifies domain-relevant objects, concepts, and actors from query
- **Relationship Mapping**: Determines connections between entities (causal, correlative, hierarchical)
- **Parameter Identification**: Extracts measurable attributes relevant to the query
- **Constraint Recognition**: Identifies limitations, boundaries, and conditions
- **Model Integration**: Synthesizes entities, relationships, and parameters into coherent model
- **Domain Knowledge Request Preparation**: Formulates specific queries for domain model

#### Domain Knowledge Functions
- **Knowledge Retrieval**: Requests domain-specific information based on query model
- **Formula Identification**: Retrieves mathematical relationships relevant to parameters
- **Model Refinement**: Enhances conceptual model with domain-specific extensions
- **Parameter Relationship Mapping**: Clarifies how parameters influence one another
- **Confidence Assessment**: Evaluates model completeness against domain requirements

#### Data Flow Description
- **Input**: Structured query package from Query Component
- **Processing**:
    1. Primary LLM extracts entities and relationships
    2. Domain LLM provides specialized knowledge and formulas
    3. Integration system combines both into unified model
- **Output**: Comprehensive knowledge model with entities, relationships, parameters, and domain context

#### LLM Interaction
- Primary LLM performs initial entity extraction and relationship mapping
- Domain LLM augments with specialized knowledge, parameter relationships, and formulas
- Model may iterate between LLMs several times for refinement

### 3. Solver Component

#### Reasoning Functions
- **Solution Strategy Selection**: Determines appropriate problem-solving approach
- **Multi-path Reasoning**: Explores multiple solution approaches simultaneously
- **Parameter Analysis**: Evaluates parameter interactions and influences
- **Formula Application**: Applies domain-specific formulas to query parameters
- **Evidence Gathering**: Collects supporting information for conclusions
- **Uncertainty Management**: Identifies and handles areas of limited knowledge
- **Reasoning Validation**: Checks logical consistency of reasoning process

#### Response Generation Functions
- **Answer Formulation**: Creates comprehensive response addressing query intent
- **Supporting Evidence Organization**: Structures evidence to support conclusions
- **Visualization Planning**: Identifies opportunities for charts or diagrams
- **Alternative Perspective Consideration**: Explores different viewpoints on the question
- **Response Variation Generation**: Creates multiple response versions with different emphasis
- **Response Selection**: Evaluates and selects optimal response variation

#### Data Flow Description
- **Input**: Structured knowledge model from Modeler Component
- **Processing**:
    1. Primary LLM applies reasoning strategies to structured model
    2. Domain LLM verifies reasoning and applies specialized techniques
    3. Integration system synthesizes reasoning paths into coherent solution
- **Output**: Solution package with reasoning steps, primary response, supporting evidence, and alternative perspectives

#### LLM Interaction
- Primary LLM handles general reasoning strategy and logical flow
- Domain LLM verifies domain-specific reasoning validity
- Tool-augmented LLM may be used for specific computational tasks

### 4. Interpreter Component

#### Response Interpretation Functions
- **Technical Translation**: Converts domain-specific terms to appropriate level
- **Narrative Construction**: Builds cohesive explanatory flow from reasoning steps
- **Clarity Enhancement**: Improves explanation clarity and readability
- **Visual Element Integration**: Incorporates charts or diagrams where helpful
- **Response Structure Organization**: Organizes information into logical sections
- **Contextual Adaptation**: Adjusts explanation based on user context

#### Quality Assessment Functions
- **Accuracy Verification**: Checks factual correctness against domain knowledge
- **Completeness Evaluation**: Verifies all query aspects are addressed
- **Clarity Assessment**: Evaluates explanation comprehensibility
- **Relevance Confirmation**: Ensures response directly addresses user query
- **Bias Detection**: Identifies and addresses potential biases in response
- **Quality Scoring**: Generates metrics for response quality dimensions

#### Data Flow Description
- **Input**: Solution package from Solver Component
- **Processing**:
    1. Primary LLM transforms technical solution into clear explanation
    2. Domain LLM verifies factual accuracy and completeness
    3. Integration system applies quality metrics and final formatting
- **Output**: Final user-facing response with appropriate formatting, visual elements, and quality metrics

#### LLM Interaction
- Primary LLM handles narrative construction and clarity enhancement
- Domain LLM provides accuracy verification
- Quality metrics may use comparison between multiple LLM evaluations

## Query-to-Model Transformation Process

The transformation from natural language query to structured model involves:

1. **Initial Parsing**: Breaking query into linguistic components
    - Subject identification: What is the query about?
    - Action identification: What is being asked about the subject?
    - Qualifier identification: What constraints or conditions apply?

2. **Domain Mapping**: Connecting linguistic components to domain concepts
    - Entity recognition: Matching text elements to domain entities
    - Relationship inference: Determining connections between entities
    - Parameter extraction: Identifying measurable aspects mentioned or implied

3. **Structure Formation**: Creating formal representation
    - Entity-relationship graph: Visual representation of interconnected concepts
    - Parameter dependency tree: Hierarchical arrangement of influencing factors
    - Constraint specification: Formal expression of limitations and conditions

4. **Domain Enhancement**: Enriching with specialized knowledge
    - Formula integration: Adding mathematical relationships
    - Parameter expansion: Including related parameters not explicitly mentioned
    - Contextual enrichment: Adding domain-specific context relevant to query

5. **Model Validation**: Ensuring model quality
    - Completeness check: Verifies all query aspects are represented
    - Consistency verification: Ensures no contradictory elements
    - Relevance assessment: Confirms model addresses original query intent

## Conceptual Data Exchange Between Components

### Query → Modeler
- Query intent classification
- Preprocessed query text
- Context information
- User history (if relevant)
- Session metadata

### Modeler → Solver
- Entity-relationship structure
- Parameter definitions and relationships
- Domain formulas and principles
- Constraints and limitations
- Confidence assessments

### Solver → Interpreter
- Reasoning steps and approach
- Primary conclusion(s)
- Supporting evidence
- Alternative perspectives
- Visualization suggestions
- Uncertainty indicators

### Interpreter → User Interface
- Structured response text
- Visual elements
- Quality metrics
- Follow-up suggestions
- Source attributions
