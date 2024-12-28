# Graph System

The graph system in emerge is responsible for representing and analyzing relationships between code components. It provides different types of graphs for various analysis needs.

## Core Components

### GraphRepresentation
The main class that encapsulates:
- A NetworkX directed graph instance
- Graph type information
- Methods for graph construction and analysis
- Metric mapping capabilities

### Graph Types

1. **Filesystem Graph**
   - Represents project directory structure
   - Maps files and folders as nodes
   - Maintains parent-child relationships

2. **Dependency Graphs**
   - **File Dependency Graph**: Shows dependencies between files
   - **Entity Dependency Graph**: Shows dependencies between entities (classes, modules)
   - Tracks import and usage relationships

3. **Inheritance Graphs**
   - Shows inheritance relationships between entities
   - Maps class hierarchies
   - Tracks interface implementations

4. **Complete Graphs**
   - Combines dependency and inheritance relationships
   - Provides comprehensive view of code structure
   - Used for complex analysis

## Features

1. **Node Management**
   - Unique node identification
   - Node property storage
   - Metric result mapping
   - Display name handling

2. **Edge Management**
   - Relationship tracking
   - Edge property storage
   - Directional relationships
   - Weight calculations

3. **Metric Integration**
   - Maps metric results to nodes
   - Supports different metric types
   - Handles local and global metrics
   - Provides filtering capabilities

4. **Graph Operations**
   - Graph composition
   - Subgraph extraction
   - Path analysis
   - Community detection

## Usage

The graph system is used throughout emerge for:
- Code structure analysis
- Dependency tracking
- Complexity measurement
- Visualization preparation

## Implementation Details

1. **Graph Creation**
   ```python
   # Create a graph representation
   graph = GraphRepresentation(graph_type)
   
   # Add nodes and relationships
   graph.add_node(node_id, properties)
   graph.add_edge(source, target)
   ```

2. **Metric Mapping**
   ```python
   # Map metrics to nodes
   graph.add_local_metric_results_to_graph_nodes(metric_results)
   ```

3. **Graph Analysis**
   ```python
   # Calculate graph metrics
   graph.calculate_dependency_graph_from_results(results)
   graph.calculate_inheritance_graph_from_results(results)
   ```

## Extension Points

The graph system can be extended through: