/**
 * API endpoint to execute Turbulance research protocols
 * Transforms the system from search-based RAG to research protocol execution
 */
export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { 
            turbulanceScript, 
            protocolName = 'UnnamedProtocol',
            executionMode = 'research_protocol',
            generateAuxiliaryFiles = true 
        } = req.body;

        // Validate required parameters
        if (!turbulanceScript || typeof turbulanceScript !== 'string') {
            return res.status(400).json({ 
                error: 'Missing or invalid turbulanceScript parameter' 
            });
        }

        // Basic Turbulance script validation
        if (!turbulanceScript.includes('proposition') || !turbulanceScript.includes('funxn')) {
            return res.status(400).json({ 
                error: 'Invalid Turbulance script format. Must include proposition and funxn definitions.' 
            });
        }

        // Log the incoming request
        console.log(`[Turbulance] Executing protocol: ${protocolName}`);
        console.log(`[Turbulance] Script length: ${turbulanceScript.length} characters`);

        // Prepare the request to the Four-Sided Triangle backend
        const backendRequest = {
            turbulance_protocol: {
                script: turbulanceScript,
                protocol_name: protocolName,
                execution_mode: executionMode,
                generate_auxiliary_files: generateAuxiliaryFiles
            },
            pipeline_config: {
                enable_metacognitive_orchestration: true,
                enable_bayesian_evidence_network: true,
                quality_thresholds: {
                    minimum_confidence: 0.8,
                    statistical_significance: 0.05
                }
            }
        };

        // Call the Four-Sided Triangle backend
        const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
        const response = await fetch(`${backendUrl}/api/turbulance/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${process.env.API_KEY || ''}`,
            },
            body: JSON.stringify(backendRequest),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('[Turbulance] Backend error:', errorData);
            
            return res.status(response.status).json({
                error: errorData.detail || errorData.error || 'Failed to execute Turbulance protocol',
                protocol_name: protocolName
            });
        }

        const resultData = await response.json();
        
        // Transform the response for frontend consumption
        const frontendResponse = {
            protocolName: protocolName,
            executionStatus: 'completed',
            interpretationResponse: {
                // Main research results
                researchFindings: resultData.research_findings || {},
                
                // Pipeline execution details
                pipelineExecution: {
                    stagesExecuted: resultData.pipeline_execution?.stages_executed || [],
                    totalExecutionTime: resultData.pipeline_execution?.total_time || 0,
                    qualityMetrics: resultData.pipeline_execution?.quality_metrics || {}
                },

                // Generated auxiliary files
                auxiliaryFiles: {
                    networkGraph: resultData.auxiliary_files?.fs_content || null,
                    resourceDependencies: resultData.auxiliary_files?.ghd_content || null,
                    decisionMemory: resultData.auxiliary_files?.hre_content || null
                },

                // Metacognitive insights
                metacognitiveInsights: {
                    resourceAllocation: resultData.metacognitive_insights?.resource_allocation || {},
                    qualityAssessment: resultData.metacognitive_insights?.quality_assessment || {},
                    optimizationDecisions: resultData.metacognitive_insights?.optimization_decisions || []
                },

                // Bayesian evidence network results
                evidenceNetwork: {
                    evidenceNodes: resultData.evidence_network?.nodes || [],
                    confidenceScores: resultData.evidence_network?.confidence_scores || {},
                    networkStructure: resultData.evidence_network?.structure || {}
                }
            },
            
            // Execution metadata
            metadata: {
                executionMode: executionMode,
                timestamp: new Date().toISOString(),
                version: '1.0.0',
                turbulanceVersion: resultData.metadata?.turbulance_version || 'unknown'
            }
        };

        console.log(`[Turbulance] Protocol executed successfully: ${protocolName}`);
        
        return res.status(200).json(frontendResponse);

    } catch (error) {
        console.error('[Turbulance] Execution error:', error);
        
        return res.status(500).json({
            error: 'Internal server error during Turbulance protocol execution',
            details: process.env.NODE_ENV === 'development' ? error.message : undefined
        });
    }
} 