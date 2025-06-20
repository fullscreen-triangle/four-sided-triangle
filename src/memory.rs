use crate::error::{FourSidedTriangleError, Result};
use crate::{memory_error, validation_error};
use dashmap::DashMap;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionState {
    pub session_id: String,
    pub original_query: String,
    pub metadata: SessionMetadata,
    pub stage_outputs: DashMap<String, serde_json::Value>,
    pub stage_metrics: DashMap<String, StageMetrics>,
    pub contextual_insights: Vec<ContextualInsight>,
    pub current_stage: u32,
    pub state: String,
    pub errors: Vec<String>,
    pub created_at: u64,
    pub updated_at: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionMetadata {
    pub timestamp: u64,
    pub user_context: serde_json::Value,
    pub query_classification: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StageMetrics {
    pub confidence: f64,
    pub processing_time: f64,
    pub refinement_iterations: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContextualInsight {
    pub insight_type: String,
    pub value: String,
    pub confidence: f64,
    pub stage: String,
}

/// High-performance session manager using DashMap for concurrent access
pub struct SessionManager {
    sessions: Arc<DashMap<String, SessionState>>,
    max_sessions: usize,
}

impl Default for SessionManager {
    fn default() -> Self {
        Self {
            sessions: Arc::new(DashMap::new()),
            max_sessions: 10000,
        }
    }
}

impl SessionManager {
    pub fn new(max_sessions: usize) -> Self {
        Self {
            sessions: Arc::new(DashMap::new()),
            max_sessions,
        }
    }

    pub fn create_session(
        &self,
        session_id: String,
        query: String,
        user_context: serde_json::Value,
        query_classification: String,
    ) -> Result<()> {
        if self.sessions.len() >= self.max_sessions {
            self.cleanup_old_sessions()?;
        }

        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        let session = SessionState {
            session_id: session_id.clone(),
            original_query: query,
            metadata: SessionMetadata {
                timestamp: now,
                user_context,
                query_classification,
            },
            stage_outputs: DashMap::new(),
            stage_metrics: DashMap::new(),
            contextual_insights: Vec::new(),
            current_stage: 0,
            state: "initialized".to_string(),
            errors: Vec::new(),
            created_at: now,
            updated_at: now,
        };

        self.sessions.insert(session_id, session);
        Ok(())
    }

    pub fn get_session(&self, session_id: &str) -> Result<Option<SessionState>> {
        if let Some(session) = self.sessions.get(session_id) {
            Ok(Some(session.clone()))
        } else {
            Ok(None)
        }
    }

    pub fn update_session_stage(
        &self,
        session_id: &str,
        stage: u32,
        output: serde_json::Value,
        metrics: StageMetrics,
    ) -> Result<()> {
        if let Some(mut session) = self.sessions.get_mut(session_id) {
            session.current_stage = stage;
            session.updated_at = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
            
            session.stage_outputs.insert(format!("stage_{}", stage), output);
            session.stage_metrics.insert(format!("stage_{}", stage), metrics);
            
            Ok(())
        } else {
            Err(memory_error!("Session not found"))
        }
    }

    pub fn add_contextual_insight(
        &self,
        session_id: &str,
        insight: ContextualInsight,
    ) -> Result<()> {
        if let Some(mut session) = self.sessions.get_mut(session_id) {
            session.contextual_insights.push(insight);
            session.updated_at = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
            Ok(())
        } else {
            Err(memory_error!("Session not found"))
        }
    }

    pub fn cleanup_old_sessions(&self) -> Result<()> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        // Remove sessions older than 1 hour
        let cutoff = now - 3600;
        
        let old_sessions: Vec<String> = self.sessions
            .iter()
            .filter(|entry| entry.value().created_at < cutoff)
            .map(|entry| entry.key().clone())
            .collect();
        
        for session_id in old_sessions {
            self.sessions.remove(&session_id);
        }
        
        Ok(())
    }

    pub fn get_session_count(&self) -> usize {
        self.sessions.len()
    }
}

// Global session manager instance
static mut GLOBAL_SESSION_MANAGER: Option<SessionManager> = None;
static INIT: std::sync::Once = std::sync::Once::new();

fn get_session_manager() -> &'static SessionManager {
    unsafe {
        INIT.call_once(|| {
            GLOBAL_SESSION_MANAGER = Some(SessionManager::default());
        });
        GLOBAL_SESSION_MANAGER.as_ref().unwrap()
    }
}

// Python FFI functions

#[pyfunction]
pub fn py_create_session(
    session_id: &str,
    query: &str,
    user_context: &str,
    query_classification: &str,
) -> PyResult<()> {
    let user_context: serde_json::Value = serde_json::from_str(user_context)?;
    let manager = get_session_manager();
    
    manager.create_session(
        session_id.to_string(),
        query.to_string(),
        user_context,
        query_classification.to_string(),
    )?;
    
    Ok(())
}

#[pyfunction]
pub fn py_update_session(
    session_id: &str,
    stage: u32,
    output: &str,
    metrics: &str,
) -> PyResult<()> {
    let output: serde_json::Value = serde_json::from_str(output)?;
    let metrics: StageMetrics = serde_json::from_str(metrics)?;
    let manager = get_session_manager();
    
    manager.update_session_stage(session_id, stage, output, metrics)?;
    Ok(())
}

#[pyfunction]
pub fn py_get_session(session_id: &str) -> PyResult<Option<String>> {
    let manager = get_session_manager();
    
    if let Some(session) = manager.get_session(session_id)? {
        let json_session = serde_json::to_string(&session)?;
        Ok(Some(json_session))
    } else {
        Ok(None)
    }
} 