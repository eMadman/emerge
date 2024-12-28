# Configuration System

The configuration system in emerge provides a flexible way to define and manage analysis settings through YAML configuration files.

## Core Components

### Configuration Class
- Main configuration handler
- Validates configuration settings
- Manages multiple analyses
- Handles project-level settings

### Configuration Enums
1. **Project Level**
   - `ConfigKeyProject`: Project-wide settings
   - `ConfigValProject`: Valid project values

2. **Analysis Level**
   - `ConfigKeyAnalysis`: Analysis configuration
   - `ConfigKeyFileScan`: File scanning options
   - `ConfigKeyEntityScan`: Entity scanning settings
   - `ConfigKeyExport`: Export configuration
   - `ConfigKeyAppConfig`: Application settings

## Configuration Structure

### 1. Project Configuration
```yaml
project:
  name: "Project Name"
  version: "1.0"
  analyses:
	- analysis1
	- analysis2
```

### 2. Analysis Configuration
```yaml
analysis:
  name: "Analysis Name"
  source-directory: "/path/to/source"
  file-scan:
	- dependency-graph
	- number-of-methods
	- source-lines-of-code
  entity-scan:
	- dependency-graph
	- inheritance-graph
  export:
	graphml: true
	d3: true
```

## Features

1. **Flexible Analysis Definition**
   - Multiple analyses per project
   - Independent analysis configurations
   - Reusable settings
   - Environment variables support

2. **Scan Configuration**
   - File-level scanning
   - Entity-level scanning
   - Language filtering
   - Directory filtering

3. **Metric Configuration**
   - Code metric selection
   - Graph metric selection
   - Metric parameters
   - Custom thresholds

4. **Export Configuration**
   - Multiple export formats
   - Output directory settings
   - Visualization options
   - Format-specific settings

## Implementation Details

1. **Configuration Loading**
   ```python
   config = Configuration(version)
   config.load_from_file(config_file)
   ```

2. **Analysis Setup**
   ```python
   analysis = config.analyses[0]
   analysis.source_directory = "/path"
   analysis.export_directory = "/output"
   ```

3. **Validation**
   - Schema validation
   - Path validation
   - Setting compatibility checks
   - Version checking

## Configuration Options

### 1. Source Control
- Git integration settings
- Repository paths
- Commit limits
- Branch selection

### 2. Language Settings
```yaml
analysis:
  languages:
	- python
	- java
	- cpp
  file-extensions:
	- .py
	- .java
	- .cpp
```

### 3. Filtering
```yaml
analysis:
  ignore-directories:
	- test
	- vendor
  ignore-files:
	- "*.test.*"
	- "*.spec.*"
```

### 4. Metric Settings
```yaml
analysis:
  metrics:
	sloc:
	  enabled: true
	fan-in-out:
	  enabled: true
	  threshold: 10
```

## Extension Points

1. **New Configuration Options**
   - Add new configuration keys
   - Implement validation
   - Define defaults
   - Add documentation

2. **Custom Validators**
   - Path validation
   - Value validation
   - Dependency checking
   - Format validation

3. **Environment Integration**
   - Environment variables
   - System settings
   - User preferences