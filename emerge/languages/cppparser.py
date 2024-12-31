"""
Contains the implementation of the C++ language parser and a relevant keyword enum.
"""

# Authors: Grzegorz Lato <grzegorz.lato@gmail.com>
# License: MIT

from typing import Dict
from enum import Enum, unique
import logging
from pathlib import Path
import os

import pyparsing as pp
import coloredlogs

from emerge.languages.abstractparser import AbstractParser, ParsingMixin, Parser, CoreParsingKeyword, LanguageType
from emerge.results import FileResult, EntityResult
from emerge.abstractresult import AbstractResult, AbstractFileResult, AbstractEntityResult
from emerge.log import Logger
from emerge.stats import Statistics

LOGGER = Logger(logging.getLogger('parser'))
coloredlogs.install(level='E', logger=LOGGER.logger(), fmt=Logger.log_format)


@unique
class CPPParsingKeyword(Enum):
    INCLUDE = "#include"
    OPEN_SCOPE = "{"
    CLOSE_SCOPE = "}"
    INLINE_COMMENT = "//"
    START_BLOCK_COMMENT = "/*"
    STOP_BLOCK_COMMENT = "*/"
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
    SEMICOLON = ";"
    TYPENAME = "typename"
    OVERRIDE = "override"


class CPPParser(AbstractParser, ParsingMixin):

    def __init__(self):
        self._results: Dict[str, AbstractResult] = {}
        self._token_mappings: Dict[str, str] = {
            ':': ' : ',
            ';': ' ; ',
            '{': ' { ',
            '}': ' } ',
            '(': ' ( ',
            ')': ' ) ',
            '[': ' [ ',
            ']': ' ] ',
            '?': ' ? ',
            '!': ' ! ',
            ',': ' , ',
            '<': ' < ',
            '>': ' > ',
            '"': ' " '
        }

    @classmethod
    def parser_name(cls) -> str:
        return Parser.CPP_PARSER.name

    @classmethod
    def language_type(cls) -> str:
        return LanguageType.CPP.name

    @property
    def results(self) -> Dict[str, AbstractResult]:
        return self._results

    @results.setter
    def results(self, value):
        self._results = value

    def generate_file_result_from_analysis(self, analysis, *, file_name: str, full_file_path: str, file_content: str) -> None:
        LOGGER.debug('generating file results...')
        scanned_tokens = self.preprocess_file_content_and_generate_token_list_by_mapping(file_content, self._token_mappings)

        # make sure to create unique names by using the relative analysis path as a base for the result
        parent_analysis_source_path = f"{Path(analysis.source_directory).parent}/"
        relative_file_path_to_analysis = full_file_path.replace(parent_analysis_source_path, "")

        file_result = FileResult.create_file_result(
            analysis=analysis,
            scanned_file_name=file_name,
            relative_file_path_to_analysis=relative_file_path_to_analysis,
            absolute_name=full_file_path,
            display_name=file_name,
            module_name="",
            scanned_by=self.parser_name(),
            scanned_language=LanguageType.CPP,
            scanned_tokens=scanned_tokens,
            source=file_content,
            preprocessed_source=""
        )

        self._add_package_name_to_result(file_result)
        self._add_imports_to_result(file_result, analysis)
        self._results[file_result.unique_name] = file_result

    def after_generated_file_results(self, analysis) -> None:
        pass

    def generate_entity_results_from_analysis(self, analysis):
        LOGGER.debug('generating entity results...')
        
        for result in self._results.values():
            if not isinstance(result, FileResult):
                continue

            # Skip implementation files for now, focus on headers
            if not result.scanned_file_name.endswith(('.h', '.hpp', '.hxx')):
                continue

            source_without_comments = self._filter_source_tokens_without_comments(
                result.scanned_tokens,
                CPPParsingKeyword.INLINE_COMMENT.value,
                CPPParsingKeyword.START_BLOCK_COMMENT.value,
                CPPParsingKeyword.STOP_BLOCK_COMMENT.value
            )

            filtered_tokens = self.preprocess_file_content_and_generate_token_list_by_mapping(
                source_without_comments, 
                self._token_mappings
            )

            current_namespace = []
            current_template_params = None
            class_scope_stack = []  # Track nested class scopes
            
            for idx, token, following in self._gen_word_read_ahead(filtered_tokens):
                if token == CPPParsingKeyword.TEMPLATE.value:
                    read_ahead = self.create_read_ahead_string(token, following)
                    
                    # Template parameter pattern
                    template_pattern = (
                        pp.Keyword(CPPParsingKeyword.TEMPLATE.value) +
                        pp.Literal('<').suppress() +
                        pp.delimitedList(
                            pp.Group(
                                pp.Optional(pp.Keyword('typename') | pp.Keyword('class')) +
                                pp.Word(pp.alphas + '_', pp.alphanums + '_')
                            )
                        ).setResultsName('params') +
                        pp.Literal('>').suppress()
                    )
                    
                    try:
                        parsed = template_pattern.parseString(read_ahead)
                        current_template_params = [param[-1] for param in parsed.params]
                        analysis.statistics.increment(Statistics.Key.PARSING_HITS)
                    except pp.ParseException as e:
                        analysis.statistics.increment(Statistics.Key.PARSING_MISSES)
                        LOGGER.warning(f'Failed to parse template declaration: {e}')
                        current_template_params = None
                        continue
                
                elif token in (CPPParsingKeyword.CLASS.value, CPPParsingKeyword.STRUCT.value):
                    read_ahead = self.create_read_ahead_string(token, following)
                    
                    # Basic class/struct pattern
                    identifier = pp.Word(pp.alphas + '_', pp.alphanums + '_')
                    template_params = pp.Optional(
                        pp.Literal('<').suppress() + 
                        pp.delimitedList(
                            pp.Word(pp.alphas + '_', pp.alphanums + '_') | 
                            pp.Literal('typename') + identifier
                        ) +
                        pp.Literal('>').suppress()
                    )
                    
                    class_pattern = (
                        pp.Keyword(token) +
                        identifier.setResultsName('name') +
                        template_params.setResultsName('template_params') +
                        pp.Optional(
                            pp.Literal(':').suppress() +
                            pp.delimitedList(
                                pp.Optional(pp.oneOf('public private protected')) +
                                pp.Word(pp.alphas + '_', pp.alphanums + '_')
                            ).setResultsName('bases')
                        )
                    )

                    try:
                        parsed = class_pattern.parseString(read_ahead)
                        
                        # Build full namespace including any enclosing classes
                        full_namespace = current_namespace.copy()
                        if class_scope_stack:
                            full_namespace.extend(class_scope_stack)

                        # Create entity result
                        entity = EntityResult.create_entity_result(
                            analysis=analysis,
                            entity_name=parsed.name,
                            entity_type=token,  # 'class' or 'struct'
                            parent_file=result,
                            namespace='::'.join(full_namespace) if full_namespace else '',
                            scanned_by=self.parser_name(),
                            scanned_language=LanguageType.CPP
                        )

                        # Track this class in the scope stack if we find an opening brace
                        for next_token in following:
                            if next_token == CPPParsingKeyword.OPEN_SCOPE.value:
                                class_scope_stack.append(parsed.name)
                                break
                            elif next_token == CPPParsingKeyword.SEMICOLON.value:
                                # Forward declaration, don't add to scope
                                break
                        
                        # Add template parameters if present
                        if current_template_params:
                            entity.template_parameters = current_template_params
                            current_template_params = None  # Reset after use
                        elif parsed.template_params:
                            entity.template_parameters = list(parsed.template_params)
                        
                        # Add base classes if present
                        if parsed.bases:
                            entity.base_types = list(parsed.bases)
                        
                        # Check for pure virtual methods to identify abstract classes
                        read_ahead_class_body = self.create_read_ahead_string('', following)
                        try:
                            # Look for virtual method declarations
                            virtual_method_pattern = (
                                pp.Keyword(CPPParsingKeyword.VIRTUAL.value) +
                                ~pp.Keyword(CPPParsingKeyword.OVERRIDE.value) +  # Not followed by override
                                pp.SkipTo(pp.oneOf([CPPParsingKeyword.SEMICOLON.value, CPPParsingKeyword.PURE_VIRTUAL.value]))
                            )
                            
                            # Find all virtual method declarations
                            virtual_methods = virtual_method_pattern.searchString(read_ahead_class_body)
                            
                            # Check if any are pure virtual (= 0)
                            if any(CPPParsingKeyword.PURE_VIRTUAL.value in str(method) for method in virtual_methods):
                                entity.is_abstract = True
                                entity.has_virtual_methods = True
                            elif virtual_methods:
                                entity.has_virtual_methods = True
                            
                        except pp.ParseException:
                            pass  # Not an abstract class
                        
                        self.create_unique_entity_name(entity)
                        result.scanned_entities.append(entity)
                        analysis.statistics.increment(Statistics.Key.PARSING_HITS)
                        
                    except pp.ParseException as e:
                        analysis.statistics.increment(Statistics.Key.PARSING_MISSES)
                        LOGGER.warning(f'Failed to parse class/struct declaration: {e}')
                        continue

                elif token == CPPParsingKeyword.NAMESPACE.value:
                    read_ahead = self.create_read_ahead_string(token, following)
                    namespace_pattern = (
                        pp.Keyword(CPPParsingKeyword.NAMESPACE.value) +
                        pp.Word(pp.alphas + '_', pp.alphanums + '_').setResultsName('name')
                    )
                    
                    try:
                        parsed = namespace_pattern.parseString(read_ahead)
                        current_namespace.append(parsed.name)
                        analysis.statistics.increment(Statistics.Key.PARSING_HITS)
                    except pp.ParseException as e:
                        analysis.statistics.increment(Statistics.Key.PARSING_MISSES)
                        LOGGER.warning(f'Failed to parse namespace declaration: {e}')
                        continue
                        
                elif token == CPPParsingKeyword.CLOSE_SCOPE.value:
                    # Check class scope first, then namespace
                    if class_scope_stack:
                        class_scope_stack.pop()
                    elif current_namespace:
                        current_namespace.pop()

    def create_unique_entity_name(self, entity: AbstractEntityResult) -> None:
        """Create a unique name for a C++ entity, including namespace and template parameters."""
        if not isinstance(entity, EntityResult):
            return

        # Start with namespace if present
        name_parts = []
        if entity.namespace:
            name_parts.append(entity.namespace)
        
        # Add the entity name
        name_parts.append(entity.entity_name)
        
        # Add template parameters if present
        if hasattr(entity, 'template_parameters') and entity.template_parameters:
            # Handle both template parameters and specializations
            template_params = []
            for param in entity.template_parameters:
                # Check if it's a specialization (contains ::)
                if '::' in param:
                    # Keep the full path for specialized types
                    template_params.append(param)
                else:
                    # For template parameters, just use the name
                    template_params.append(param.split('::')[-1])
            
            template_str = f"<{','.join(template_params)}>"
            name_parts[-1] = name_parts[-1] + template_str
            
            # Store the original template parameter string for reference
            entity.template_signature = template_str
        
        # Create the unique name
        entity.unique_name = '::'.join(name_parts)
        
        # Set display name (without full namespace path)
        entity.display_name = entity.entity_name
        if hasattr(entity, 'template_parameters') and entity.template_parameters:
            # Use simplified template parameters for display
            simple_params = [p.split('::')[-1] for p in entity.template_parameters]
            entity.display_name += f"<{','.join(simple_params)}>"

    def _add_imports_to_result(self, result: AbstractFileResult, analysis):
        LOGGER.debug(f'extracting imports from file result {result.scanned_file_name}...')
        list_of_words_with_newline_strings = result.scanned_tokens
        
        source_string_no_comments = self._filter_source_tokens_without_comments(
            list_of_words_with_newline_strings,
            CPPParsingKeyword.INLINE_COMMENT.value,
            CPPParsingKeyword.START_BLOCK_COMMENT.value,
            CPPParsingKeyword.STOP_BLOCK_COMMENT.value
        )

        filtered_list_no_comments = self.preprocess_file_content_and_generate_token_list_by_mapping(source_string_no_comments, self._token_mappings)

        for _, obj, following in self._gen_word_read_ahead(filtered_list_no_comments):
            if obj == CPPParsingKeyword.INCLUDE.value:
                read_ahead_string = self.create_read_ahead_string(obj, following)

                include_name = pp.Word(pp.alphanums + CoreParsingKeyword.DOT.value + CoreParsingKeyword.SLASH.value +
                                       CoreParsingKeyword.DOUBLE_QUOTE.value + CoreParsingKeyword.UNDERSCORE.value)

                expression_to_match = pp.Keyword(CPPParsingKeyword.INCLUDE.value) + \
                    pp.ZeroOrMore(pp.Suppress(CoreParsingKeyword.OPENING_ANGLE_BRACKET.value) |
                                  pp.Suppress(CoreParsingKeyword.CLOSING_ANGLE_BRACKET.value) |
                                  pp.Suppress(CoreParsingKeyword.DOUBLE_QUOTE.value)) + \
                    include_name.setResultsName(CoreParsingKeyword.IMPORT_ENTITY_NAME.value)

                try:
                    parsing_result = expression_to_match.parseString(read_ahead_string)
                except pp.ParseException as exception:
                    result.analysis.statistics.increment(Statistics.Key.PARSING_MISSES)
                    LOGGER.warning(f'warning: could not parse result {result=}\n{exception}')
                    LOGGER.warning(f'next tokens: {[obj] + following[:ParsingMixin.Constants.MAX_DEBUG_TOKENS_READAHEAD.value]}')
                    continue

                analysis.statistics.increment(Statistics.Key.PARSING_HITS)

                # ignore any dependency substring from the config ignore list
                dependency = getattr(parsing_result, CoreParsingKeyword.IMPORT_ENTITY_NAME.value)

                # try to resolve the dependency
                resolved_dependency = self.try_resolve_dependency(dependency, result, analysis)

                if self._is_dependency_in_ignore_list(resolved_dependency, analysis):
                    LOGGER.debug(f'ignoring dependency from {result.unique_name} to {resolved_dependency}')
                else:
                    result.scanned_import_dependencies.append(resolved_dependency)
                    LOGGER.debug(f'adding import: {resolved_dependency}')

    def try_resolve_dependency(self, dependency: str, result: AbstractFileResult, analysis) -> str:
        resolved_dependency = self.resolve_relative_dependency_path(dependency, str(result.absolute_dir_path), analysis.source_directory)
        check_dependency_path = f"{ Path(analysis.source_directory).parent}/{resolved_dependency}"
        if os.path.exists(check_dependency_path):
            dependency = resolved_dependency
        return dependency

    def _add_package_name_to_result(self, result: FileResult):
        result.module_name = ""


if __name__ == "__main__":
    LEXER = CPPParser()
    print(f'{LEXER.results=}')
