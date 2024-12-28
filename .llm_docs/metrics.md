# Metrics System

The metrics system in emerge is designed to analyze and measure different aspects of codebases. It provides both code-level and graph-level metrics through a flexible and extensible architecture.

## Architecture

The metrics system is built on two main abstract base classes:

1. `AbstractCodeMetric` - Base class for metrics that analyze code content
2. `AbstractGraphMetric` - Base class for metrics that analyze graph structures

These are implemented in concrete classes through `CodeMetric` and `GraphMetric` which provide common functionality like metric naming.

## Available Metrics

### Code Metrics

1. **Source Lines of Code (SLOC)**
   - Counts actual lines of code, excluding comments and whitespace
   - Available at both file and entity level
   - Provides local metrics per file/entity and global metrics for the codebase

2. **Number of Methods**
   - Counts method definitions in code
   - Available at both file and entity level
   - Helps measure code complexity

3. **Whitespace Complexity**
   - Alternative to SLOC that analyzes whitespace patterns
   - Based on Adam Tornhill's approach
   - Useful for estimating code complexity

4. **TF-IDF**
   - Analyzes semantic content of code
   - Extracts keywords based on their importance
   - Helps understand the domain concepts in code

5. **Git Metrics** 
   - Analyzes repository history
   - Tracks code churn, author count, etc.
   - Integrates with other metrics for historical perspective

### Graph Metrics

1. **Fan-in/Fan-out**
   - Measures dependencies between components
   - Available for:
	 - Dependency graphs
	 - Inheritance graphs
	 - Complete graphs
   - Helps identify highly coupled components

2. **Louvain Modularity**
   - Detects community structures in dependency graphs
   - Helps identify natural code clusters
   - Available for all graph types

## Implementation Details

1. **Metric Results**
   - Metrics are stored in two forms:
	 - Local metrics (per file/entity)
	 - Global metrics (codebase-wide)
   - Results are attached to nodes in graph representations

2. **Export Formats**
   - Console output (prettified tables)
   - JSON files
   - D3.js compatible format for visualization

3. **Integration**
   - Metrics are calculated during analysis
   - Results can be filtered by graph type
   - Metrics can be combined for advanced analysis (e.g., git history with complexity)

## Extending the System

New metrics can be added by:

1. Inheriting from appropriate base class (`CodeMetric` or `GraphMetric`)
2. Implementing required methods:
   - `metric_name`
   - `pretty_metric_name`
   - `calculate_from_results`

The system will automatically integrate new metrics into the analysis pipeline and export functionality.