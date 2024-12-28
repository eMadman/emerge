# Analysis Engine

The analysis engine is the core component of emerge that orchestrates the entire analysis process. It consists of two main classes: `Analyzer` and `Analysis`.

## Architecture Overview

### Analyzer
The `Analyzer` class is the main orchestrator that:
- Manages the overall analysis process
- Coordinates between configuration, parsers, and analyses
- Triggers the different phases of analysis
- Collects and aggregates results

### Analysis
The `Analysis` class represents a single analysis configuration and:
- Holds configuration settings
- Manages metrics and results
- Handles graph representations
- Controls export formats

## Analysis Process

The analysis process follows these key steps:

1. **Initialization**
   - Analyzer is created with configuration and parsers
   - Each analysis is configured with specific settings
   - Analysis timer starts

2. **Filesystem Graph Creation**
   - Creates a graph representation of the project structure
   - Filters files based on configured extensions
   - Handles symlinks and directory structures
   - Builds initial node relationships

3. **Result Generation**
   - **File Results**: 
	 - Scans files matching configured extensions
	 - Parses content using appropriate language parsers
	 - Creates file-level results
   
   - **Entity Results** (if configured):
	 - Extracts entities from file results
	 - Creates entity-level results
	 - Builds relationships between entities

4. **Metric Calculation**
   - **Code Metrics**:
	 - Calculates metrics for files and entities
	 - Aggregates local and global results
	 - Tracks calculation statistics
   
   - **Graph Metrics**:
	 - Creates necessary graph representations
	 - Calculates graph-based metrics
	 - Maps metrics to graph nodes

5. **Result Processing**
   - Collects metrics from all analyses
   - Aggregates statistics
   - Prepares data for export

6. **Export**
   - Exports results in configured formats:
	 - GraphML
	 - D3.js visualizations
	 - Tabular formats (console/file)
	 - JSON data
   - Generates final statistics

## Key Features

1. **Flexible Configuration**
   - Multiple analyses can be configured
   - Each analysis can have different settings
   - Configurable file/directory filters
   - Language-specific settings

2. **Metric System Integration**
   - Supports both code and graph metrics
   - Extensible metric calculation system
   - Local and global metric results
   - Runtime performance tracking

3. **Graph Representations**
   - Multiple graph types supported:
	 - Filesystem graph
	 - Dependency graphs
	 - Inheritance graphs
	 - Complete graphs
   - Automatic graph creation and linking

4. **Performance Monitoring**
   - Detailed timing statistics
   - Resource usage tracking
   - Progress logging
   - Performance metrics

## Extending the Engine

The analysis engine can be extended through:

1. **New Metrics**
   - Implement `AbstractCodeMetric` or `AbstractGraphMetric`
   - Add metric calculation logic
   - Register with analysis configuration

2. **New Parsers**
   - Implement `AbstractParser`
   - Add language-specific parsing logic
   - Register parser for file extensions

3. **New Export Formats**
   - Add export logic to Analysis class
   - Implement format-specific transformations
   - Configure in analysis settings

## Usage Example

```python
# Create analyzer with configuration and parsers
analyzer = Analyzer(config, parsers)

# Start analysis process
analyzer.start_analyzing()

# Analysis will:
# 1. Create filesystem graph
# 2. Generate results
# 3. Calculate metrics
# 4. Export results
```

The analysis engine provides a robust and extensible foundation for code analysis, supporting various languages, metrics, and output formats while maintaining performance and flexibility.