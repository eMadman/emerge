# C++ Entity Handling Implementation Plan

## Overview
This implementation plan outlines the steps needed to add C++ entity handling capabilities to the emerge codebase, following the patterns established in the Java implementation while respecting C++'s unique characteristics.

## Current State Analysis
- C++ parser exists with basic include dependency tracking
- No class/inheritance tracking implemented
- Key C++ patterns observed in sample code:
  - Pure virtual (abstract) base classes
  - Public inheritance
  - Header/implementation file separation
  - Multiple inheritance support needed
  - Template class support needed
  - Namespace organization

## Implementation Phases

### Phase 1: Header File Entity Detection
**Files Affected:**
- `/emerge/emerge/languages/cppparser.py`

**Steps:**
1. Add C++ specific parsing keywords to `CPPParsingKeyword`:
   ```python
   CLASS = "class"
   STRUCT = "struct"
   NAMESPACE = "namespace"
   VIRTUAL = "virtual"
   PUBLIC = "public"
   PRIVATE = "private"
   PROTECTED = "protected"
   TEMPLATE = "template"
   COLON = ":"
   PURE_VIRTUAL = "= 0"
   ```

2. Implement header file entity detection:
   - Parse class/struct declarations with pyparsing
   - Handle template class declarations
   - Support pure virtual method detection
   - Create basic entity results

3. Implement `create_unique_entity_name`:
   - Use namespace as module prefix
   - Include template parameters in name
   - Handle nested class names

### Phase 2: Inheritance and Virtual Methods
**Files Affected:**
- `/emerge/emerge/languages/cppparser.py`

**Steps:**
1. Add inheritance parsing:
   ```python
   # Example pattern to match
   class_inheritance = (
       pp.Keyword("class") +
       pp.Word(pp.alphas) +
       pp.Optional(
           pp.Keyword(":") +
           pp.Optional(pp.oneOf("public private protected")) +
           pp.delimitedList(pp.Word(pp.alphas))
       )
   )
   ```

2. Implement `_add_inheritance_to_entity_result`:
   - Track base classes with access specifiers
   - Support multiple inheritance
   - Handle virtual inheritance
   - Parse pure virtual methods

3. Update entity result generation:
   - Link derived classes to base classes
   - Track virtual method overrides
   - Handle abstract class detection

### Phase 3: Header/Implementation Correlation
**Files Affected:**
- `/emerge/emerge/languages/cppparser.py`

**Steps:**
1. Enhance file result processing:
   - Match .h and .cpp files
   - Correlate method implementations
   - Track include dependencies between them

2. Update dependency tracking:
   - Link header and source files
   - Track forward declarations
   - Handle template instantiations

### Phase 4: Testing and Validation
**Files Affected:**
- `/emerge/emerge/languages/cppparser.py`
- `/workspace/emerge/test/test_cpp_parser.py` (new)

**Steps:**
1. Create test suite with real C++ patterns:
   ```cpp
   // Test cases to cover
   namespace foo {
     template<typename T>
     class Base {
       virtual void method() = 0;
     };
     
     class Derived : public Base<int> {
       void method() override;
     };
   }
   ```

2. Validate entity detection:
   - Test namespace handling
   - Verify inheritance tracking
   - Check template support
   - Validate virtual method detection

## Implementation Guidelines

### Entity Recognition Strategy
1. Header File Priority:
   - Primary entity detection from .h/.hpp files
   - Use implementation files (.cpp) only for dependency validation
   - Handle inline methods in header files

2. Entity Categories:
   - Primary: classes, structs
   - Scoping: namespaces
   - Relationships: inheritance, template instantiation
   - Virtual interface detection
   - Nested classes (e.g., `KnownDevice` inside `SensorDataFactory`)
   - Smart pointer usage (e.g., `std::shared_ptr<SensorData>`)
   - STL container relationships (e.g., `std::vector<KnownDevice*>`)

3. Naming Convention:
   ```cpp
   // Input:
   namespace networking {
     template<typename T>
     class Connection {
       struct Config {};
     };
   }
   
   // Entity Names:
   "networking::Connection<T>"
   "networking::Connection<T>::Config"
   ```

### Inheritance Analysis
1. Base Class Resolution:
   ```cpp
   class Derived : 
     public Base1,
     protected Base2,
     private Base3
   ```
   - Track each base class with its access specifier
   - Support virtual inheritance
   - Handle forward declarations

2. Virtual Method Detection:
   ```cpp
   class Interface {
     virtual void method1() = 0;  // Pure virtual
     virtual void method2();      // Virtual
     void method3() override;     // Override
   };
   ```

3. Template Handling:
   - Track template class declarations
   - Record template parameter names
   - Link template instantiations to base template

### Dependency Tracking
1. Include Resolution:
   ```cpp
   #include <vector>           // STL include
   #include <memory>          // Smart pointer include
   #include "myclass.h"       // Project include
   #include "../base/utils.h" // Relative include
   ```

2. Implementation Correlation:
   - Match .h and .cpp files
   - Track include graph
   - Resolve relative paths
   - Link template instantiations

3. STL and Smart Pointer Dependencies:
   ```cpp
   class Factory {
     std::vector<Device*> devices;                    // Container relationship
     std::shared_ptr<Base> create();                  // Smart pointer relationship
     std::unique_ptr<Config> config;                  // Ownership relationship
     std::map<std::string, std::any> properties;      // Complex STL usage
   };
   ```

4. External Library Dependencies:
   - Track system includes (<>) vs project includes ("")
   - Handle platform-specific headers
   - Support third-party library includes (e.g., NimBLEUUID)

### Limitations and Scope
1. In Scope:
   - Class/struct declarations
   - Inheritance relationships
   - Namespace organization
   - Template class declarations
   - Pure virtual interface detection
   - Header/implementation file correlation
   - STL container relationships
   - Smart pointer dependencies
   - Nested class hierarchies
   - Static member tracking
   - Forward declarations

2. Out of Scope:
   - Template metaprogramming analysis
   - Function body parsing
   - Macro expansion
   - Friend relationships
   - Operator overloading
   - Anonymous namespaces
   - Template specialization details
   - SFINAE patterns
   - Compile-time constant evaluation
   - Platform-specific preprocessor branches

## Success Criteria
1. Entity Detection:
   - Accurate class/struct identification
   - Proper namespace scoping
   - Template class support
   - Nested class handling
   - Smart pointer usage detection
   - STL container relationships

2. Relationship Tracking:
   - Multiple inheritance support
   - Virtual method detection
   - Template instantiation linking
   - Include dependency resolution
   - Header/implementation correlation
   - Forward declaration handling

3. Integration:
   - Proper graph generation
   - Consistent with Java parser patterns
   - Efficient parsing performance
   - Memory usage optimization
   - STL dependency tracking
   - External library support

4. Testing Coverage:
   ```cpp
   // Must handle all patterns:
   namespace outer {
     namespace inner {
       template<typename T>
       class Base {
         virtual ~Base() = default;
         virtual T process() = 0;
       protected:
         class Context {};
         static std::shared_ptr<Base<T>> create();
       };
       
       class Derived : public Base<int> {
         int process() override;
         std::vector<std::unique_ptr<Context>> contexts;
       };
     }
   }
   ```

5. Real-world Validation:
   - Parse SmartSpin2k codebase successfully
   - Handle all observed C++ patterns
   - Generate accurate dependency graphs
   - Support STL and smart pointer relationships
   - Track template instantiations correctly

## Next Steps
1. Begin with Phase 1 implementation
2. Create test cases for each pattern
3. Validate against real C++ codebases
4. Document C++-specific features