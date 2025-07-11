//! Turbulance DSL Parser
//! 
//! High-performance Rust parser for Turbulance research protocol syntax.
//! Supports complete parsing of:
//! - proposition/hypothesis definitions
//! - pipeline_stage() calls
//! - funxn definitions
//! - conditional logic (given/ensure)
//! - data source declarations
//! - computational expressions

use crate::error::{FourSidedTriangleError, Result};
use crate::{validation_error};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use regex::Regex;
use once_cell::sync::Lazy;

// Global parser instance for statistics tracking
static GLOBAL_PARSER: Lazy<Arc<Mutex<TurbulanceParser>>> = Lazy::new(|| {
    Arc::new(Mutex::new(TurbulanceParser::new()))
});

/// Types of nodes in the parsed Turbulance AST
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum NodeType {
    Proposition,
    Hypothesis, 
    PipelineStage,
    Function,
    Conditional,
    DataSource,
    Variable,
    Comment,
    Expression,
}

/// Parsed Turbulance node in the AST
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TurbulanceNode {
    pub node_type: NodeType,
    pub line_number: usize,
    pub content: String,
    pub name: Option<String>,
    pub parameters: HashMap<String, TurbulanceValue>,
    pub children: Vec<TurbulanceNode>,
    pub dependencies: Vec<String>,
}

/// Values in Turbulance scripts
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TurbulanceValue {
    String(String),
    Number(f64),
    Boolean(bool),
    Array(Vec<TurbulanceValue>),
    Object(HashMap<String, TurbulanceValue>),
    PipelineCall {
        stage: String,
        config: HashMap<String, TurbulanceValue>,
    },
}

/// Complete parsed Turbulance script
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TurbulanceScript {
    pub protocol_name: String,
    pub nodes: Vec<TurbulanceNode>,
    pub propositions: Vec<TurbulanceNode>,
    pub pipeline_calls: Vec<TurbulanceNode>,
    pub functions: Vec<TurbulanceNode>,
    pub data_sources: Vec<TurbulanceNode>,
    pub variables: HashMap<String, TurbulanceValue>,
    pub dependencies: HashMap<String, Vec<String>>,
}

/// High-performance Turbulance parser
pub struct TurbulanceParser {
    // Compiled regex patterns for performance
    proposition_regex: Regex,
    hypothesis_regex: Regex,
    pipeline_stage_regex: Regex,
    function_regex: Regex,
    conditional_regex: Regex,
    data_source_regex: Regex,
    variable_regex: Regex,
    comment_regex: Regex,
    
    // Parser statistics
    lines_parsed: usize,
    protocols_parsed: usize,
    parse_errors: usize,
}

impl Default for TurbulanceParser {
    fn default() -> Self {
        Self::new()
    }
}

impl TurbulanceParser {
    pub fn new() -> Self {
        Self {
            proposition_regex: Regex::new(r"^proposition\s+(\w+):").unwrap(),
            hypothesis_regex: Regex::new(r#"motion\s+Hypothesis\("([^"]+)"\)"#).unwrap(),
            pipeline_stage_regex: Regex::new(r#"(\w+)\s*=\s*pipeline_stage\(\s*"([^"]+)"\s*(?:,\s*\{([^}]*)\})?\s*\)"#).unwrap(),
            function_regex: Regex::new(r"^funxn\s+(\w+)\(([^)]*)\):").unwrap(),
            conditional_regex: Regex::new(r"(given|ensure|alternatively)\s+(.+):").unwrap(),
            data_source_regex: Regex::new(r#"(local|domain_expert|external_api)\("([^"]+)"\)"#).unwrap(),
            variable_regex: Regex::new(r"(\w+)\s*=\s*(.+)").unwrap(),
            comment_regex: Regex::new(r"^\s*//.*").unwrap(),
            
            lines_parsed: 0,
            protocols_parsed: 0,
            parse_errors: 0,
        }
    }

    /// Parse a complete Turbulance script
    pub fn parse_script(&mut self, script_content: &str, protocol_name: &str) -> Result<TurbulanceScript> {
        let lines: Vec<&str> = script_content.lines().collect();
        self.lines_parsed += lines.len();
        
        let mut script = TurbulanceScript {
            protocol_name: protocol_name.to_string(),
            nodes: Vec::new(),
            propositions: Vec::new(),
            pipeline_calls: Vec::new(),
            functions: Vec::new(),
            data_sources: Vec::new(),
            variables: HashMap::new(),
            dependencies: HashMap::new(),
        };

        let mut context_stack = Vec::new();
        let mut indentation_stack = Vec::new();
        let mut current_parent: Option<usize> = None;

        for (line_num, line) in lines.iter().enumerate() {
            let line_number = line_num + 1;
            let trimmed_line = line.trim();
            
            if trimmed_line.is_empty() || self.comment_regex.is_match(trimmed_line) {
                if !trimmed_line.is_empty() {
                    let comment_node = TurbulanceNode {
                        node_type: NodeType::Comment,
                        line_number,
                        content: trimmed_line.to_string(),
                        name: None,
                        parameters: HashMap::new(),
                        children: Vec::new(),
                        dependencies: Vec::new(),
                    };
                    script.nodes.push(comment_node);
                }
                continue;
            }

            // Track indentation for nested structures
            let indentation = line.len() - line.trim_start().len();
            current_parent = self.update_parent_context(
                &mut context_stack,
                &mut indentation_stack,
                indentation,
                current_parent,
            );

            match self.parse_line(trimmed_line, line_number) {
                Ok(mut node) => {
                    // Handle nested structures
                    if let Some(parent_idx) = current_parent {
                        if parent_idx < script.nodes.len() {
                            script.nodes[parent_idx].children.push(node.clone());
                        }
                    }

                    // Categorize nodes
                    match node.node_type {
                        NodeType::Proposition => {
                            context_stack.push(script.nodes.len());
                            indentation_stack.push(indentation);
                            current_parent = Some(script.nodes.len());
                            script.propositions.push(node.clone());
                        }
                        NodeType::PipelineStage => {
                            script.pipeline_calls.push(node.clone());
                            if let Some(name) = &node.name {
                                // Extract dependencies and convert to PipelineCall value
                                let deps = self.extract_dependencies(&node.parameters);
                                script.dependencies.insert(name.clone(), deps);
                                
                                // Create PipelineCall value
                                if let Some(TurbulanceValue::String(stage)) = node.parameters.get("stage") {
                                    let config = if let Some(TurbulanceValue::Object(cfg)) = node.parameters.get("config") {
                                        cfg.clone()
                                    } else {
                                        HashMap::new()
                                    };
                                    
                                    let pipeline_call = TurbulanceValue::PipelineCall {
                                        stage: stage.clone(),
                                        config,
                                    };
                                    script.variables.insert(name.clone(), pipeline_call);
                                }
                            }
                        }
                        NodeType::Function => {
                            context_stack.push(script.nodes.len());
                            indentation_stack.push(indentation);
                            current_parent = Some(script.nodes.len());
                            script.functions.push(node.clone());
                        }
                        NodeType::DataSource => {
                            script.data_sources.push(node.clone());
                        }
                        NodeType::Variable => {
                            if let Some(name) = &node.name {
                                if let Some(value) = node.parameters.get("value") {
                                    script.variables.insert(name.clone(), value.clone());
                                }
                            }
                        }
                        NodeType::Conditional => {
                            if indentation > 0 {
                                context_stack.push(script.nodes.len());
                                indentation_stack.push(indentation);
                                current_parent = Some(script.nodes.len());
                            }
                        }
                        _ => {}
                    }

                    script.nodes.push(node);
                }
                Err(e) => {
                    self.parse_errors += 1;
                    eprintln!("Parse error at line {}: {}", line_number, e);
                    // Continue parsing despite errors
                }
            }
        }

        self.protocols_parsed += 1;
        Ok(script)
    }

    /// Update parent context based on indentation
    fn update_parent_context(
        &self,
        context_stack: &mut Vec<usize>,
        indentation_stack: &mut Vec<usize>,
        current_indentation: usize,
        current_parent: Option<usize>,
    ) -> Option<usize> {
        // Pop contexts if we've dedented
        while let Some(&last_indentation) = indentation_stack.last() {
            if current_indentation <= last_indentation {
                indentation_stack.pop();
                context_stack.pop();
            } else {
                break;
            }
        }

        context_stack.last().copied()
    }

    /// Parse a single line into a TurbulanceNode
    fn parse_line(&self, line: &str, line_number: usize) -> Result<TurbulanceNode> {
        // Comment
        if self.comment_regex.is_match(line) {
            return Ok(TurbulanceNode {
                node_type: NodeType::Comment,
                line_number,
                content: line.to_string(),
                name: None,
                parameters: HashMap::new(),
                children: Vec::new(),
                dependencies: Vec::new(),
            });
        }

        // Proposition
        if let Some(captures) = self.proposition_regex.captures(line) {
            let name = captures.get(1).unwrap().as_str();
            return Ok(TurbulanceNode {
                node_type: NodeType::Proposition,
                line_number,
                content: line.to_string(),
                name: Some(name.to_string()),
                parameters: HashMap::new(),
                children: Vec::new(),
                dependencies: Vec::new(),
            });
        }

        // Hypothesis
        if let Some(captures) = self.hypothesis_regex.captures(line) {
            let hypothesis = captures.get(1).unwrap().as_str();
            let mut parameters = HashMap::new();
            parameters.insert("hypothesis".to_string(), TurbulanceValue::String(hypothesis.to_string()));
            
            return Ok(TurbulanceNode {
                node_type: NodeType::Hypothesis,
                line_number,
                content: line.to_string(),
                name: None,
                parameters,
                children: Vec::new(),
                dependencies: Vec::new(),
            });
        }

        // Pipeline stage
        if let Some(captures) = self.pipeline_stage_regex.captures(line) {
            let var_name = captures.get(1).unwrap().as_str();
            let stage_name = captures.get(2).unwrap().as_str();
            let config_str = captures.get(3).map(|m| m.as_str()).unwrap_or("");

            let mut parameters = HashMap::new();
            parameters.insert("stage".to_string(), TurbulanceValue::String(stage_name.to_string()));
            
            if !config_str.is_empty() {
                let config = self.parse_config_object(config_str)?;
                parameters.insert("config".to_string(), TurbulanceValue::Object(config));
            }

            return Ok(TurbulanceNode {
                node_type: NodeType::PipelineStage,
                line_number,
                content: line.to_string(),
                name: Some(var_name.to_string()),
                parameters,
                children: Vec::new(),
                dependencies: Vec::new(),
            });
        }

        // Function definition
        if let Some(captures) = self.function_regex.captures(line) {
            let func_name = captures.get(1).unwrap().as_str();
            let params_str = captures.get(2).unwrap().as_str();
            
            let mut parameters = HashMap::new();
            if !params_str.is_empty() {
                let params = self.parse_parameter_list(params_str)?;
                parameters.insert("parameters".to_string(), TurbulanceValue::Array(params));
            }

            return Ok(TurbulanceNode {
                node_type: NodeType::Function,
                line_number,
                content: line.to_string(),
                name: Some(func_name.to_string()),
                parameters,
                children: Vec::new(),
                dependencies: Vec::new(),
            });
        }

        // Conditional logic
        if let Some(captures) = self.conditional_regex.captures(line) {
            let condition_type = captures.get(1).unwrap().as_str();
            let condition = captures.get(2).unwrap().as_str();
            
            let mut parameters = HashMap::new();
            parameters.insert("condition_type".to_string(), TurbulanceValue::String(condition_type.to_string()));
            parameters.insert("condition".to_string(), TurbulanceValue::String(condition.to_string()));

            return Ok(TurbulanceNode {
                node_type: NodeType::Conditional,
                line_number,
                content: line.to_string(),
                name: None,
                parameters,
                children: Vec::new(),
                dependencies: Vec::new(),
            });
        }

        // Data source
        if let Some(captures) = self.data_source_regex.captures(line) {
            let source_type = captures.get(1).unwrap().as_str();
            let source_name = captures.get(2).unwrap().as_str();
            
            let mut parameters = HashMap::new();
            parameters.insert("source_type".to_string(), TurbulanceValue::String(source_type.to_string()));
            parameters.insert("source_name".to_string(), TurbulanceValue::String(source_name.to_string()));

            return Ok(TurbulanceNode {
                node_type: NodeType::DataSource,
                line_number,
                content: line.to_string(),
                name: Some(source_name.to_string()),
                parameters,
                children: Vec::new(),
                dependencies: Vec::new(),
            });
        }

        // Variable assignment
        if let Some(captures) = self.variable_regex.captures(line) {
            let var_name = captures.get(1).unwrap().as_str();
            let value_str = captures.get(2).unwrap().as_str();
            
            let mut parameters = HashMap::new();
            let value = self.parse_value(value_str)?;
            parameters.insert("value".to_string(), value);

            return Ok(TurbulanceNode {
                node_type: NodeType::Variable,
                line_number,
                content: line.to_string(),
                name: Some(var_name.to_string()),
                parameters,
                children: Vec::new(),
                dependencies: Vec::new(),
            });
        }

        // Fallback: treat as expression
        Ok(TurbulanceNode {
            node_type: NodeType::Expression,
            line_number,
            content: line.to_string(),
            name: None,
            parameters: HashMap::new(),
            children: Vec::new(),
            dependencies: Vec::new(),
        })
    }

    /// Parse a configuration object string with better error handling
    fn parse_config_object(&self, config_str: &str) -> Result<HashMap<String, TurbulanceValue>> {
        let mut config = HashMap::new();
        let mut bracket_depth = 0;
        let mut in_quotes = false;
        let mut current_pair = String::new();
        let mut escape_next = false;

        for ch in config_str.chars() {
            if escape_next {
                current_pair.push(ch);
                escape_next = false;
                continue;
            }

            match ch {
                '\\' => {
                    escape_next = true;
                    current_pair.push(ch);
                }
                '"' => {
                    in_quotes = !in_quotes;
                    current_pair.push(ch);
                }
                '{' | '[' if !in_quotes => {
                    bracket_depth += 1;
                    current_pair.push(ch);
                }
                '}' | ']' if !in_quotes => {
                    bracket_depth -= 1;
                    current_pair.push(ch);
                }
                ',' if !in_quotes && bracket_depth == 0 => {
                    self.parse_config_pair(&current_pair.trim(), &mut config)?;
                    current_pair.clear();
                }
                _ => {
                    current_pair.push(ch);
                }
            }
        }

        // Handle the last pair
        if !current_pair.trim().is_empty() {
            self.parse_config_pair(&current_pair.trim(), &mut config)?;
        }

        Ok(config)
    }

    /// Parse a single configuration key-value pair
    fn parse_config_pair(&self, pair: &str, config: &mut HashMap<String, TurbulanceValue>) -> Result<()> {
        if let Some(colon_pos) = pair.find(':') {
            let key = pair[..colon_pos].trim().trim_matches('"').trim_matches('\'');
            let value_str = pair[colon_pos + 1..].trim();
            
            let value = self.parse_value(value_str)?;
            config.insert(key.to_string(), value);
        }
        
        Ok(())
    }

    /// Parse a parameter list
    fn parse_parameter_list(&self, params_str: &str) -> Result<Vec<TurbulanceValue>> {
        let mut params = Vec::new();
        
        for param in params_str.split(',') {
            let param = param.trim();
            if !param.is_empty() {
                params.push(TurbulanceValue::String(param.to_string()));
            }
        }
        
        Ok(params)
    }

    /// Parse a value from string representation with improved handling
    fn parse_value(&self, value_str: &str) -> Result<TurbulanceValue> {
        let trimmed = value_str.trim();
        
        // String literal
        if (trimmed.starts_with('"') && trimmed.ends_with('"')) ||
           (trimmed.starts_with('\'') && trimmed.ends_with('\'')) {
            return Ok(TurbulanceValue::String(trimmed[1..trimmed.len()-1].to_string()));
        }
        
        // Boolean
        if trimmed == "true" {
            return Ok(TurbulanceValue::Boolean(true));
        }
        if trimmed == "false" {
            return Ok(TurbulanceValue::Boolean(false));
        }
        
        // Number
        if let Ok(num) = trimmed.parse::<f64>() {
            return Ok(TurbulanceValue::Number(num));
        }
        
        // Array
        if trimmed.starts_with('[') && trimmed.ends_with(']') {
            let array_content = &trimmed[1..trimmed.len()-1];
            let mut array = Vec::new();
            let mut bracket_depth = 0;
            let mut in_quotes = false;
            let mut current_item = String::new();
            let mut escape_next = false;

            for ch in array_content.chars() {
                if escape_next {
                    current_item.push(ch);
                    escape_next = false;
                    continue;
                }

                match ch {
                    '\\' => {
                        escape_next = true;
                        current_item.push(ch);
                    }
                    '"' => {
                        in_quotes = !in_quotes;
                        current_item.push(ch);
                    }
                    '[' | '{' if !in_quotes => {
                        bracket_depth += 1;
                        current_item.push(ch);
                    }
                    ']' | '}' if !in_quotes => {
                        bracket_depth -= 1;
                        current_item.push(ch);
                    }
                    ',' if !in_quotes && bracket_depth == 0 => {
                        if !current_item.trim().is_empty() {
                            array.push(self.parse_value(&current_item.trim())?);
                        }
                        current_item.clear();
                    }
                    _ => {
                        current_item.push(ch);
                    }
                }
            }

            // Handle the last item
            if !current_item.trim().is_empty() {
                array.push(self.parse_value(&current_item.trim())?);
            }
            
            return Ok(TurbulanceValue::Array(array));
        }
        
        // Object
        if trimmed.starts_with('{') && trimmed.ends_with('}') {
            let object_content = &trimmed[1..trimmed.len()-1];
            let config = self.parse_config_object(object_content)?;
            return Ok(TurbulanceValue::Object(config));
        }
        
        // Default to string
        Ok(TurbulanceValue::String(trimmed.to_string()))
    }

    /// Extract dependencies from pipeline stage parameters
    fn extract_dependencies(&self, parameters: &HashMap<String, TurbulanceValue>) -> Vec<String> {
        let mut dependencies = Vec::new();
        
        // Look for references to other variables in the config
        if let Some(TurbulanceValue::Object(config)) = parameters.get("config") {
            for value in config.values() {
                self.extract_dependencies_from_value(value, &mut dependencies);
            }
        }
        
        dependencies
    }

    /// Recursively extract dependencies from values
    fn extract_dependencies_from_value(&self, value: &TurbulanceValue, dependencies: &mut Vec<String>) {
        match value {
            TurbulanceValue::String(s) => {
                // Look for variable references (simple heuristic)
                if s.chars().all(|c| c.is_alphanumeric() || c == '_') && 
                   s.chars().next().map_or(false, |c| c.is_alphabetic()) {
                    dependencies.push(s.clone());
                }
            }
            TurbulanceValue::Array(arr) => {
                for item in arr {
                    self.extract_dependencies_from_value(item, dependencies);
                }
            }
            TurbulanceValue::Object(obj) => {
                for val in obj.values() {
                    self.extract_dependencies_from_value(val, dependencies);
                }
            }
            TurbulanceValue::PipelineCall { config, .. } => {
                for val in config.values() {
                    self.extract_dependencies_from_value(val, dependencies);
                }
            }
            _ => {}
        }
    }

    /// Get parser statistics
    pub fn get_statistics(&self) -> HashMap<String, f64> {
        let mut stats = HashMap::new();
        stats.insert("lines_parsed".to_string(), self.lines_parsed as f64);
        stats.insert("protocols_parsed".to_string(), self.protocols_parsed as f64);
        stats.insert("parse_errors".to_string(), self.parse_errors as f64);
        
        let error_rate = if self.lines_parsed > 0 {
            self.parse_errors as f64 / self.lines_parsed as f64
        } else {
            0.0
        };
        stats.insert("error_rate".to_string(), error_rate);
        
        stats
    }
}

// Python FFI functions using global parser state

#[pyfunction]
pub fn py_parse_turbulance_script(script_content: &str, protocol_name: &str) -> PyResult<String> {
    let mut parser = GLOBAL_PARSER.lock().unwrap();
    let script = parser.parse_script(script_content, protocol_name)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    serde_json::to_string(&script)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
}

#[pyfunction]
pub fn py_validate_turbulance_syntax(script_content: &str) -> PyResult<bool> {
    let mut parser = TurbulanceParser::new();
    match parser.parse_script(script_content, "validation") {
        Ok(_) => Ok(true),
        Err(_) => Ok(false),
    }
}

#[pyfunction]
pub fn py_get_parser_statistics() -> PyResult<String> {
    let parser = GLOBAL_PARSER.lock().unwrap();
    let stats = parser.get_statistics();
    
    serde_json::to_string(&stats)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
} 