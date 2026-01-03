# 🏛️ BHIV Central Depository - Enterprise AI Truth Engine

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com/)
[![Redis](https://img.shields.io/badge/Redis-7.0+-red.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🧠 Executive Summary

**BHIV Central Depository** is an enterprise-grade **Truth Engine** designed as the foundational data vault for AI Avatar/Assistant platforms. It provides constitutional governance, immutable storage, and complete audit trails for AI-generated content with legal defensibility.

### Core Value Proposition
```
AI Avatar/Assistant Platform × BHIV Bucket = Enterprise-Grade AI Foundation
```

### Key Differentiators
- **Constitutional Governance**: Immutable rules with hierarchical authority
- **AI Firewall**: Prevents AI logic contamination in storage layer
- **Complete Provenance**: Every artifact has traceable lineage
- **Legal Compliance**: Enterprise-ready audit trails
- **Zero Trust Architecture**: AI can write, but never depends on bucket

## 🏗️ System Architecture

### 🏛️ **BHIV Bucket Core Components**

#### 1. **Constitutional Lock System**
- **Immutable Governance**: Once locked, constitutional rules cannot be changed
- **Authority Hierarchy**: Data Sovereign → Strategic Advisor → Executor → AI Agent
- **Rule Enforcement**: Automatic validation of all system operations
- **Compliance Tracking**: Complete audit trail of governance decisions

#### 2. **Truth Engine**
- **Immutable Storage**: All changes create new versions, never overwrite existing data
- **Provenance Tracking**: Complete parent-child relationships with cryptographic integrity
- **Artifact Validation**: Constitutional compliance checking before storage
- **Version Management**: Automatic versioning with detailed change tracking
- **Tombstone System**: Constitutional deletion with audit trail preservation

#### 3. **AI Integration Firewall**
- **Contamination Prevention**: Blocks AI reasoning logic from permanent storage
- **Artifact Sanitization**: Removes AI uncertainty markers and temporal confusion
- **Feedback Loop Prevention**: Stops AI from modifying its own historical outputs
- **Hallucination Filtering**: Validates AI outputs before constitutional storage
- **Schema Enforcement**: Ensures only approved artifact classes are stored

#### 4. **Governance System**
- **Authority Validation**: Real-time enforcement of who can perform what actions
- **Escalation Procedures**: Automatic escalation to higher authority when needed
- **Decision Tracking**: Complete governance audit trail with timestamps
- **Constitutional Compliance**: Ensures all actions follow immutable rules
- **Conflict Resolution**: Structured decision-making with clear authority chains

#### 5. **Custodianship System**
- **Formal Ownership**: Establishes clear Data Sovereign authority
- **Baseline Management**: Captures and protects immutable system state
- **Integration Boundaries**: Validates and controls AI system integration points
- **Retention Policies**: Defines comprehensive data lifecycle management
- **Compliance Reporting**: Automated generation of regulatory compliance reports

#### 6. **Gatekeeping System**
- **Integration Control**: Prevents unauthorized system integrations
- **Executor Enforcement**: Manages and validates execution permissions
- **Escalation Protocol**: Structured advisory consultation procedures
- **Drift Prevention**: Blocks unauthorized changes to system configuration
- **Security Validation**: Multi-layer security checks for all operations

### 🤖 **AI Agent Ecosystem**

#### Agent Registry & Discovery
- **Dynamic Registration**: Automatic agent discovery and capability detection
- **Standardized Interface**: Consistent input/output format across all agents
- **Domain Classification**: Agents organized by functional domains
- **Capability Mapping**: Detailed specification of agent capabilities
- **Version Control**: Agent versioning with backward compatibility

#### Available Agent Domains
- **Financial**: `cashflow_analyzer`, `financial_coordinator`, `goal_recommender`
- **Automotive**: `auto_diagnostics`, `vehicle_maintenance`, `fuel_efficiency`
- **Legal**: `law_agent` (basic, adaptive, enhanced modes)
- **Educational**: `gurukul_*` agents, `vedic_quiz_agent`, `sanskrit_parser`
- **Workflow**: `schedule_agent`, `workflow_agent`
- **Content**: `textToJson`, `suggestion_bot`

### 🧺 **Intelligent Basket Orchestration**
- **Multi-Agent Workflows**: Chain multiple AI agents with constitutional protection
- **Data Flow Management**: Seamless data passing with complete provenance tracking
- **Execution Strategies**: Sequential, parallel, and conditional execution patterns
- **Constitutional Compliance**: All workflow executions stored in Truth Engine
- **Error Handling**: Comprehensive error recovery and rollback mechanisms

## 🚀 Installation & Setup

### System Requirements
- **Python**: 3.11+ (recommended for optimal performance)
- **MongoDB**: 6.0+ (Truth Engine storage)
- **Redis**: 7.0+ (high-performance caching)
- **Node.js**: 18+ (admin panel)
- **Memory**: 8GB+ RAM recommended
- **Storage**: 50GB+ for production deployments

### Quick Installation
```bash
# Clone repository
git clone https://github.com/your-org/BHIV_Central_Depository.git
cd BHIV_Central_Depository

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Install admin panel
cd admin-panel && npm install && cd ..
```

### Environment Configuration
```env
# Database Configuration (Required)
MONGODB_URI=mongodb://localhost:27017/bhiv_bucket
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# AI Service API Keys
OPENAI_API_KEY=sk-your-openai-key
GROQ_API_KEY=gsk_your-groq-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Server Configuration
FASTAPI_PORT=8000
LOG_LEVEL=INFO

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret
ENCRYPTION_KEY=your-encryption-key

# Optional: Supabase Integration
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### System Startup
```bash
# Start Truth Engine (Primary Service)
python main.py

# Start Admin Panel (Optional)
cd admin-panel && npm run dev

# Verify System Health
curl http://localhost:8000/health
```

## 🎯 API Reference

### Core System Endpoints

#### Health & Status
```http
GET /health                    # System health check
GET /bucket/status            # BHIV Bucket status
GET /bucket/constitutional    # Constitutional lock status
```

#### Agent Management
```http
GET /agents                   # List all available agents
GET /agents?domain={domain}   # Filter agents by domain
POST /run-agent              # Execute single agent
```

#### Basket Orchestration
```http
GET /baskets                 # List available baskets
POST /run-basket            # Execute agent workflow
POST /create-basket         # Create new workflow
DELETE /baskets/{name}      # Delete basket with cleanup
```

#### Truth Engine Operations
```http
GET /bucket/artifacts/{id}           # Retrieve artifact
GET /bucket/artifacts/{id}/lineage   # Get artifact ancestry
POST /bucket/artifacts/{id}/version  # Create new version
DELETE /bucket/artifacts/{id}        # Create tombstone
```

#### Governance & Authority
```http
GET /governance/status               # Governance system status
POST /governance/validate           # Validate authority action
POST /governance/escalate           # Escalate decision
GET /governance/decisions           # Decision history
```

#### Custodianship (Data Sovereign Only)
```http
GET /custodianship/status                    # Ownership status
POST /custodianship/baseline                # Capture system baseline
GET /custodianship/integration-boundaries   # Validate AI boundaries
GET /custodianship/retention-posture        # Data retention policies
```

#### Gatekeeping & Security
```http
POST /gatekeeping/integration-request    # Evaluate integration
POST /gatekeeping/executor-validation   # Validate executor action
POST /gatekeeping/escalation-evaluation # Evaluate escalation need
GET /gatekeeping/status                 # Complete security status
```

### Agent Execution Examples

#### Financial Analysis
```bash
curl -X POST http://localhost:8000/run-agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "cashflow_analyzer",
    "input_data": {
      "transactions": [
        {"id": 1, "amount": 1000, "type": "income"},
        {"id": 2, "amount": -500, "type": "expense"}
      ]
    }
  }'
```

#### Workflow Optimization
```bash
curl -X POST http://localhost:8000/run-basket \
  -H "Content-Type: application/json" \
  -d '{
    "basket_name": "workflow_optimizer",
    "input_data": {
      "task": "Optimize financial reporting process",
      "priority": "high"
    }
  }'
```

#### Legal Query Processing
```bash
curl -X POST http://localhost:8000/enhanced-query \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "What are my rights regarding wrongful termination?",
    "location": "California, USA"
  }'
```

## 🏛️ Authority & Governance

### Authority Hierarchy

#### **Data Sovereign** (Ashmit Pandey)
- **Ultimate Authority**: Constitutional changes, schema approval, deployment control
- **Responsibilities**: System custodian, gatekeeper, drift-prevention authority
- **Powers**: Override any decision, modify constitutional rules, control integrations
- **Accountability**: Final responsibility for system integrity and compliance

#### **Strategic Advisor** (Vijay Dhawan)
- **Advisory Role**: Strategic guidance, escalation resolution, technical consultation
- **Authority**: Approve escalations, provide recommendations, access all artifacts
- **Boundaries**: Advisory only, no constitutional authority, no parallel power structure
- **Expertise**: Technical architecture, business strategy, risk assessment

#### **Executor** (Akanksha Pandey)
- **Execution Role**: Day-to-day operations, approved actions, routine maintenance
- **Permissions**: Execute baskets, create artifacts, generate reports
- **Restrictions**: Cannot modify constitution, requires approval for system changes
- **Responsibilities**: Operational excellence, routine monitoring, user support

#### **AI Agents**
- **Write-Only Access**: Can create artifacts through firewall validation
- **Restrictions**: Cannot modify existing data, no governance access, no self-modification
- **Protection**: All outputs processed through AI Integration Firewall
- **Isolation**: Complete separation from storage layer decision-making

### Constitutional Rules (IMMUTABLE)

1. **Immutability Principle**: No data can be silently overwritten or modified
2. **Provenance Requirement**: Every artifact must have complete traceable lineage
3. **AI Separation Rule**: AI can WRITE to Bucket, Bucket never DEPENDS on AI
4. **Authority Supremacy**: Data Sovereign has final authority over all storage decisions
5. **Truth Preservation**: Bucket stores only constitutionally validated artifacts
6. **Constitutional Supremacy**: Constitutional rules override product urgency or convenience

## 🔧 Development Guide

### Adding New AI Agents

#### 1. Agent Structure Setup
```bash
mkdir -p agents/your_agent_name
cd agents/your_agent_name
```

#### 2. Agent Specification (`agent_spec.json`)
```json
{
  "name": "your_agent_name",
  "domains": ["your_domain"],
  "module_path": "agents.your_agent_name.your_agent_name",
  "capabilities": {
    "chainable": true,
    "memory_access": false,
    "async_processing": true
  },
  "input_schema": {
    "required": ["input_field"],
    "properties": {
      "input_field": {
        "type": "string",
        "description": "Primary input parameter",
        "validation": "^[a-zA-Z0-9\\s]+$"
      }
    }
  },
  "output_schema": {
    "properties": {
      "result": {"type": "object"},
      "status": {"type": "string"},
      "metadata": {"type": "object"}
    }
  },
  "sample_input": {
    "input_field": "sample value"
  },
  "sample_output": {
    "result": {"processed": true},
    "status": "completed",
    "metadata": {"execution_time": "0.5s"}
  }
}
```

#### 3. Agent Implementation (`your_agent_name.py`)
```python
from typing import Dict, Any
from utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

async def process(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent processing function with constitutional compliance.
    All outputs automatically processed through BHIV Bucket firewall.
    
    Args:
        input_data: Validated input data matching agent specification
        
    Returns:
        Dict containing processing results with required metadata
    """
    try:
        # Input validation
        required_field = input_data.get("input_field")
        if not required_field:
            return {"error": "Missing required input_field"}
        
        # Core processing logic
        result = {
            "processed_data": f"Processed: {required_field}",
            "timestamp": datetime.now().isoformat(),
            "agent_version": "1.0.0"
        }
        
        # Return standardized response
        return {
            "result": result,
            "status": "completed",
            "metadata": {
                "execution_time": "0.5s",
                "input_hash": hash(str(input_data)),
                "constitutional_compliance": True
            }
        }
        
    except Exception as e:
        logger.error(f"Agent processing error: {e}")
        return {
            "error": str(e),
            "status": "failed",
            "metadata": {"error_type": type(e).__name__}
        }
```

### Creating Custom Baskets

#### Basket Configuration (`baskets/your_basket.json`)
```json
{
  "basket_name": "your_custom_workflow",
  "description": "Custom multi-agent workflow",
  "agents": ["agent1", "agent2", "agent3"],
  "execution_strategy": "sequential",
  "data_flow": {
    "agent1": {"output_to": "agent2"},
    "agent2": {"output_to": "agent3"},
    "agent3": {"final_output": true}
  },
  "error_handling": {
    "strategy": "rollback",
    "retry_count": 3,
    "timeout": 300
  },
  "constitutional_requirements": {
    "authority_level": "executor",
    "audit_trail": true,
    "immutable_storage": true
  }
}
```

## 📊 System Monitoring

### Health Check Verification
```bash
# Basic health check
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "services": {
    "mongodb": "connected",
    "redis": "connected",
    "socketio": "disabled"
  },
  "bhiv_bucket": {
    "status": "active",
    "constitutional_lock": true,
    "truth_engine": "operational",
    "ai_firewall": "active"
  }
}
```

### Performance Metrics
```bash
# Redis performance
curl http://localhost:8000/redis/status

# Governance statistics
curl http://localhost:8000/governance/status

# Execution logs
curl http://localhost:8000/execution-logs/{execution_id}
```

### Constitutional Status Verification
```bash
curl http://localhost:8000/bucket/constitutional

# Expected response
{
  "version": "1.0.0",
  "locked": true,
  "constitution_hash": "sha256:abc123...",
  "integrity_verified": true,
  "last_modified": "2024-01-01T00:00:00Z",
  "authority": "data_sovereign"
}
```

## 🚨 Security & Compliance

### Security Features
- **Zero Trust Architecture**: No implicit trust between components
- **Constitutional Enforcement**: Immutable rules with cryptographic integrity
- **Authority Validation**: Real-time permission checking
- **Audit Trail**: Complete logging of all system operations
- **Data Encryption**: At-rest and in-transit encryption
- **Input Sanitization**: Comprehensive input validation and sanitization

### Compliance Standards
- **SOC 2 Type II**: Security, availability, processing integrity
- **GDPR**: Data protection and privacy rights
- **HIPAA**: Healthcare information protection (when applicable)
- **SOX**: Financial reporting controls
- **ISO 27001**: Information security management

### Emergency Procedures

#### Constitutional Crisis Response
```bash
# 1. Immediate system lock
curl -X POST http://localhost:8000/emergency/lock

# 2. Verify constitutional integrity
curl http://localhost:8000/bucket/constitutional

# 3. Contact Data Sovereign immediately
# 4. Initiate recovery procedures
```

#### Authority Breach Protocol
```bash
# 1. Activate emergency governance
curl -X POST http://localhost:8000/governance/emergency

# 2. Audit all recent decisions
curl http://localhost:8000/governance/decisions?limit=1000

# 3. Escalate to Strategic Advisor
# 4. Implement corrective measures
```

## 📈 Success Metrics

### Constitutional Compliance KPIs
- ✅ **100% Immutability**: Zero silent overwrites detected
- ✅ **Complete Provenance**: All artifacts have traceable lineage
- ✅ **Authority Enforcement**: 100% compliance with authority hierarchy
- ✅ **AI Separation**: Zero AI logic contamination in storage layer
- ✅ **Truth Preservation**: Only constitutionally validated artifacts stored

### System Performance Metrics
- **Uptime**: 99.9% availability target
- **Response Time**: <200ms for agent execution
- **Throughput**: 1000+ concurrent agent executions
- **Storage Efficiency**: Optimized artifact compression
- **Audit Completeness**: 100% operation logging

### Business Impact Indicators
- **Regulatory Compliance**: Zero compliance violations
- **Legal Defensibility**: Complete audit trail availability
- **Risk Mitigation**: Proactive threat detection and response
- **Operational Efficiency**: Automated governance and monitoring
- **Scalability**: Linear performance scaling with load

## 🔮 Roadmap & Future Development

### Phase 1: Foundation (✅ Complete)
- Constitutional lock implementation
- Truth engine deployment
- AI firewall activation
- Governance system launch
- Custodianship establishment
- Gatekeeping system activation

### Phase 2: Enhancement (🚧 In Progress)
- Advanced analytics dashboard
- Automated compliance reporting
- Multi-tenant architecture
- Global artifact distribution
- Enhanced security monitoring
- Performance optimization

### Phase 3: Enterprise Scale (📋 Planned)
- Kubernetes orchestration
- Multi-region deployment
- Advanced AI capabilities
- Blockchain integration
- Regulatory automation
- Enterprise SLA management

### Phase 4: Monetization (🔮 Future)
- Artifact marketplace
- Usage-based billing
- IP licensing system
- White-label solutions
- Professional services
- Training and certification

## 🤝 Contributing

### Development Standards
- **Code Quality**: 90%+ test coverage required
- **Documentation**: Comprehensive API documentation
- **Security**: Security review for all changes
- **Constitutional Compliance**: All changes must pass constitutional validation
- **Performance**: Benchmark testing required

### Contribution Process
1. Fork repository and create feature branch
2. Implement changes with comprehensive tests
3. Ensure constitutional compliance
4. Submit pull request with detailed description
5. Pass security and performance reviews
6. Obtain Data Sovereign approval for constitutional changes

## 📞 Support & Contact

### Technical Support
- **Documentation**: [docs.bhiv-central.com](https://docs.bhiv-central.com)
- **API Reference**: [api.bhiv-central.com](https://api.bhiv-central.com)
- **Community Forum**: [community.bhiv-central.com](https://community.bhiv-central.com)
- **Issue Tracker**: [GitHub Issues](https://github.com/your-org/BHIV_Central_Depository/issues)

### Authority Contacts
- **Data Sovereign**: Ashmit Pandey - ashmit@bhiv-central.com
- **Strategic Advisor**: Vijay Dhawan - vijay@bhiv-central.com
- **Executor**: Akanksha Pandey - akanksha@bhiv-central.com

---

## 🏛️ **Constitutional Declaration**

*This BHIV Bucket system is hereby established as the foundational Truth Engine for AI operations. The constitutional rules defined herein are immutable and shall govern all data operations with cryptographic integrity. The Data Sovereign maintains ultimate authority over this system, with clear escalation procedures for all governance decisions.*

*By using this system, all parties acknowledge and agree to abide by the constitutional framework and authority hierarchy established herein. This system provides enterprise-grade AI infrastructure with complete legal defensibility and regulatory compliance.*

**System Specifications**:
- **Version**: 1.0.0
- **Constitutional Hash**: Immutable
- **Authority**: Data Sovereign (Ashmit Pandey)
- **Compliance**: SOC 2, GDPR, HIPAA, SOX, ISO 27001
- **Status**: ✅ Production Ready
- **Deployment**: Enterprise-Grade

---

*BHIV Central Depository - Where AI meets Constitutional Data Governance* 🏛️