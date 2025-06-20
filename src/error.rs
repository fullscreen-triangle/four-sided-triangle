use pyo3::prelude::*;
use thiserror::Error;

pub type Result<T> = std::result::Result<T, FourSidedTriangleError>;

#[derive(Error, Debug)]
pub enum FourSidedTriangleError {
    #[error("Bayesian calculation error: {message}")]
    BayesianError { message: String },

    #[error("Text processing error: {message}")]
    TextProcessingError { message: String },

    #[error("Memory management error: {message}")]
    MemoryError { message: String },

    #[error("Throttle detection error: {message}")]
    ThrottleDetectionError { message: String },

    #[error("Quality assessment error: {message}")]
    QualityAssessmentError { message: String },

    #[error("Optimization error: {message}")]
    OptimizationError { message: String },

    #[error("Configuration error: {message}")]
    ConfigurationError { message: String },

    #[error("Serialization error: {message}")]
    SerializationError { message: String },

    #[error("Validation error: {message}")]
    ValidationError { message: String },

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("JSON error: {0}")]
    JsonError(#[from] serde_json::Error),

    #[error("Mathematical error: division by zero or invalid operation")]
    MathematicalError,

    #[error("Concurrent access error: {message}")]
    ConcurrencyError { message: String },

    #[error("Resource exhaustion: {message}")]
    ResourceError { message: String },
}

impl From<FourSidedTriangleError> for PyErr {
    fn from(err: FourSidedTriangleError) -> PyErr {
        match err {
            FourSidedTriangleError::BayesianError { message } => {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Bayesian Error: {}", message))
            }
            FourSidedTriangleError::TextProcessingError { message } => {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Text Processing Error: {}", message))
            }
            FourSidedTriangleError::MemoryError { message } => {
                PyErr::new::<pyo3::exceptions::PyMemoryError, _>(format!("Memory Error: {}", message))
            }
            FourSidedTriangleError::ThrottleDetectionError { message } => {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Throttle Detection Error: {}", message))
            }
            FourSidedTriangleError::QualityAssessmentError { message } => {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Quality Assessment Error: {}", message))
            }
            FourSidedTriangleError::OptimizationError { message } => {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Optimization Error: {}", message))
            }
            FourSidedTriangleError::ConfigurationError { message } => {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Configuration Error: {}", message))
            }
            FourSidedTriangleError::SerializationError { message } => {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Serialization Error: {}", message))
            }
            FourSidedTriangleError::ValidationError { message } => {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Validation Error: {}", message))
            }
            FourSidedTriangleError::IoError(io_err) => {
                PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("IO Error: {}", io_err))
            }
            FourSidedTriangleError::JsonError(json_err) => {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON Error: {}", json_err))
            }
            FourSidedTriangleError::MathematicalError => {
                PyErr::new::<pyo3::exceptions::PyArithmeticError, _>("Mathematical Error: Division by zero or invalid operation")
            }
            FourSidedTriangleError::ConcurrencyError { message } => {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Concurrency Error: {}", message))
            }
            FourSidedTriangleError::ResourceError { message } => {
                PyErr::new::<pyo3::exceptions::PyMemoryError, _>(format!("Resource Error: {}", message))
            }
        }
    }
}

// Convenience macros for creating errors
#[macro_export]
macro_rules! bayesian_error {
    ($msg:expr) => {
        FourSidedTriangleError::BayesianError {
            message: $msg.to_string(),
        }
    };
}

#[macro_export]
macro_rules! text_processing_error {
    ($msg:expr) => {
        FourSidedTriangleError::TextProcessingError {
            message: $msg.to_string(),
        }
    };
}

#[macro_export]
macro_rules! memory_error {
    ($msg:expr) => {
        FourSidedTriangleError::MemoryError {
            message: $msg.to_string(),
        }
    };
}

#[macro_export]
macro_rules! throttle_error {
    ($msg:expr) => {
        FourSidedTriangleError::ThrottleDetectionError {
            message: $msg.to_string(),
        }
    };
}

#[macro_export]
macro_rules! quality_error {
    ($msg:expr) => {
        FourSidedTriangleError::QualityAssessmentError {
            message: $msg.to_string(),
        }
    };
}

#[macro_export]
macro_rules! optimization_error {
    ($msg:expr) => {
        FourSidedTriangleError::OptimizationError {
            message: $msg.to_string(),
        }
    };
}

#[macro_export]
macro_rules! validation_error {
    ($msg:expr) => {
        FourSidedTriangleError::ValidationError {
            message: $msg.to_string(),
        }
    };
} 