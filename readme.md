# 🏛️ BHIV Central Depository - Truth Engine for AI Avatar Platform

## 🧠 What This System Really Is

**BHIV Central Depository** is the foundational **Truth Engine** for AI Avatar/Assistant platforms. It serves as the constitutional data vault that stores everything AI systems ever produce with immutable integrity.

This system combines:
```
AI Avatar/Assistant Platform × BHIV Bucket = Enterprise-Grade AI Foundation
```

The BHIV Bucket is not just storage - it's a **Truth Engine** that guarantees:
- **Immutable History** - No silent overwrites ever
- **Provenance Tracking** - Every artifact has traceable lineage  
- **Constitutional Authority** - Data Sovereign controls all storage decisions
- **AI Logic Separation** - AI can WRITE to Bucket, Bucket never DEPENDS on AI
- **Legal Defensibility** - Complete audit trail for enterprise compliance

## 🏗️ System Architecture

### 🏛️ **BHIV Bucket Components**

#### 1. **Constitutional Lock**
- **Immutable Rules**: Once locked, constitutional rules cannot be changed
- **Authority Hierarchy**: Data Sovereign → Strategic Advisor → Executor → AI Agent
- **Truth Preservation**: Enforces fundamental laws of the system

#### 2. **Truth Engine**
- **Immutable Storage**: All changes create new versions, never overwrite
- **Provenance Tracking**: Complete parent-child relationships
- **Artifact Validation**: Constitutional compliance checking
- **Version Management**: Automatic versioning with change tracking

#### 3. **AI Integration Firewall**
- **Contamination Prevention**: Blocks AI logic from storage layer
- **Artifact Sanitization**: Removes AI reasoning from permanent storage
- **Feedback Loop Prevention**: Stops AI from modifying its own past
- **Hallucination Filtering**: Prevents uncertain AI outputs from storage

#### 4. **Governance System**
- **Authority Validation**: Enforces who can do what
- **Escalation Procedures**: Automatic escalation to higher authority
- **Decision Tracking**: Complete governance audit trail
- **Constitutional Compliance**: Ensures all actions follow constitutional rules

#### 5. **Custodianship System**
- **Formal Ownership**: Establishes Data Sovereign authority
- **Baseline Management**: Captures and protects system state
- **Integration Boundaries**: Validates AI system integration
- **Retention Policies**: Defines data lifecycle management

#### 6. **Gatekeeping System**
- **Integration Control**: Prevents unauthorized system integrations
- **Executor Enforcement**: Manages execution permissions
- **Escalation Protocol**: Structured advisory consultation
- **Drift Prevention**: Blocks unauthorized changes

### 🤖 **AI Agent System**
- **Dynamic Discovery**: Automatic agent registration and capability detection
- **Standardized Interface**: Consistent input/output format across all agents
- **Constitutional Processing**: All AI outputs processed through firewall

### 🧺 **Intelligent Basket Orchestration**
- **Multi-Agent Workflows**: Chain multiple AI agents with constitutional protection
- **Data Flow Management**: Seamless data passing with provenance tracking
- **Execution Strategies**: Sequential execution with immutable logging
- **Constitutional Compliance**: All executions stored in Truth Engine

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (Recommended: 3.11+)
- **MongoDB** (for Truth Engine storage)
- **Redis** (for high-performance caching)
- **Node.js 16+** (for admin panel)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd BHIV_Central_Depository

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database URLs and API keys

# Install admin panel dependencies
cd admin-panel
npm install
cd ..
```

### Environment Setup
Create a `.env` file in the root directory:
```env
# Database Configuration (Required for Truth Engine)
MONGODB_URI=mongodb://localhost:27017/bhiv_bucket
REDIS_HOST=localhost
REDIS_PORT=6379

# Supabase Configuration (Optional)
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# AI Service API Keys
OPENAI_API_KEY=sk-your-openai-key
GROQ_API_KEY=gsk_your-groq-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Server Configuration
FASTAPI_PORT=8000
```

### Start the System
```bash
# Start the BHIV Bucket Truth Engine
python main.py

# In another terminal, start the admin panel
cd admin-panel
npm run dev
```

## 🎯 Core API Endpoints

### **BHIV Bucket Truth Engine**
```bash
# System Status
GET /health                           # Complete system health
GET /bucket/status                    # BHIV Bucket status
GET /bucket/constitutional            # Constitutional lock status

# Artifact Management
GET /bucket/artifacts/{id}            # Retrieve artifact
GET /bucket/artifacts/{id}/lineage    # Get artifact ancestry
POST /bucket/artifacts/{id}/version   # Create new version
DELETE /bucket/artifacts/{id}         # Create tombstone

# Governance & Authority
GET /governance/status                # Governance system status
POST /governance/validate             # Validate authority action
POST /governance/escalate             # Escalate decision
GET /governance/decisions             # Decision history

# Custodianship (Data Sovereign Only)
GET /custodianship/status             # Formal ownership status
POST /custodianship/baseline          # Capture system baseline
GET /custodianship/integration-boundaries  # Validate AI boundaries
GET /custodianship/retention-posture  # Data retention policies

# Gatekeeping & Integration Control
POST /gatekeeping/integration-request # Evaluate integration
POST /gatekeeping/executor-validation # Validate executor action
POST /gatekeeping/escalation-evaluation # Evaluate escalation need
GET /gatekeeping/status               # Complete gatekeeping status

# Owner Responsibility
POST /owner/responsibility-confirmation # Confirm constitutional commitment
```

### **AI Agent System (Legacy Compatible)**
```bash
# Agent Operations
GET /agents                           # List all agents
POST /run-agent                       # Execute single agent
GET /baskets                          # List available baskets
POST /run-basket                      # Execute agent workflow
POST /create-basket                   # Create new workflow
```

## 🏛️ Authority Hierarchy

### **Data Sovereign** (Ashmit Pandey)
- **Ultimate Authority**: Constitutional changes, schema approval, deployment control
- **Responsibilities**: Custodian, Gatekeeper, Drift-Prevention Authority
- **Powers**: Can override any decision, modify constitutional rules, control integrations

### **Strategic Advisor** (Vijay Dhawan)
- **Advisory Role**: Strategic guidance, escalation resolution, technical consultation
- **Authority**: Can approve escalations, provide recommendations, access all artifacts
- **Boundaries**: Advisory only, no constitutional authority, no parallel power

### **Executor** (Akanksha Pandey)
- **Execution Role**: Day-to-day operations, approved actions, routine maintenance
- **Permissions**: Execute baskets, create artifacts, generate reports
- **Restrictions**: Cannot modify constitution, requires approval for system changes

### **AI Agents**
- **Write-Only Access**: Can create artifacts through firewall validation
- **Restrictions**: Cannot modify existing data, no governance access, no self-modification
- **Protection**: All outputs processed through AI Integration Firewall

## 🛡️ Constitutional Rules (IMMUTABLE)

1. **Immutability**: No data can be silently overwritten
2. **Provenance**: Every artifact must have traceable lineage  
3. **AI Separation**: AI can WRITE to Bucket, Bucket never DEPENDS on AI
4. **Authority Hierarchy**: Data Sovereign has final authority over storage
5. **Truth Preservation**: Bucket stores only verifiable artifacts
6. **Constitutional Supremacy**: Constitutional rules override product urgency

## 🔧 Adding New AI Agents

### Step 1: Create Agent Structure
```bash
mkdir -p agents/your_agent_name
cd agents/your_agent_name
```

### Step 2: Agent Specification
Create `agent_spec.json`:
```json
{
    "name": "your_agent_name",
    "domains": ["your_domain"],
    "module_path": "agents.your_agent_name.your_agent_name",
    "capabilities": {
        "chainable": true,
        "memory_access": false
    },
    "input_schema": {
        "required": ["input_field"],
        "properties": {
            "input_field": {
                "type": "string",
                "description": "Input description"
            }
        }
    },
    "sample_input": {
        "input_field": "sample value"
    }
}
```

### Step 3: Agent Implementation
Create `your_agent_name.py`:
```python
from typing import Dict
from utils.logger import get_logger

logger = get_logger(__name__)

async def process(input_data: Dict) -> Dict:
    """
    Agent processing function with constitutional compliance
    All outputs automatically processed through BHIV Bucket firewall
    """
    try:
        # Your agent logic here
        result = {
            "output": "processed_data",
            "status": "completed"
        }
        
        logger.info("Agent processing completed")
        return result
        
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return {"error": str(e)}
```

## 📊 System Verification

### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "mongodb": "connected",
    "redis": "connected"
  },
  "bhiv_bucket": {
    "status": "active",
    "constitutional_lock": true,
    "truth_engine": "operational",
    "ai_firewall": "active"
  }
}
```

### Constitutional Status
```bash
curl http://localhost:8000/bucket/constitutional
```

Expected response:
```json
{
  "version": "1.0.0",
  "locked": true,
  "constitution_hash": "sha256...",
  "integrity_verified": true
}
```

## 🎯 Use Cases

### **Enterprise AI Deployment**
- **Legal Compliance**: Complete audit trail for regulatory requirements
- **IP Protection**: Immutable provenance for intellectual property
- **Version Control**: Track all AI model outputs and changes
- **Risk Management**: Constitutional rules prevent data corruption

### **AI Avatar/Assistant Platform**
- **User Interactions**: Immutable history of all conversations
- **Persona Evolution**: Track how AI personalities develop over time
- **Content Creation**: Provenance tracking for generated media
- **Monetization**: Clear ownership and usage rights

## 🚨 Emergency Procedures

### Constitutional Crisis
If constitutional integrity is compromised:
1. **Immediate**: Stop all AI operations
2. **Assess**: Check `/bucket/constitutional` endpoint
3. **Escalate**: Contact Data Sovereign immediately
4. **Restore**: Use immutable backup procedures

### Authority Breach
If unauthorized access detected:
1. **Lock**: Activate emergency constitutional lock
2. **Audit**: Review `/governance/decisions` endpoint
3. **Escalate**: Immediate escalation to Data Sovereign
4. **Investigate**: Full authority validation audit

## 📈 Success Metrics

### **Constitutional Compliance**
- ✅ **100% Immutability**: No silent overwrites ever
- ✅ **Complete Provenance**: Every artifact traceable
- ✅ **Authority Enforcement**: All actions properly authorized
- ✅ **AI Separation**: No AI logic in storage layer
- ✅ **Truth Preservation**: Only verified artifacts stored

### **System Health**
- ✅ **Backward Compatibility**: All existing functionality preserved
- ✅ **Performance**: Constitutional protection with no degradation
- ✅ **Reliability**: Constitutional rules prevent corruption
- ✅ **Scalability**: Ready for enterprise deployment
- ✅ **Auditability**: Complete governance trail

## 🔮 Roadmap

### **Phase 1: Foundation** (✅ Complete)
- Constitutional lock implementation
- Truth engine deployment
- AI firewall activation
- Governance system launch
- Custodianship establishment
- Gatekeeping system activation

### **Phase 2: Enhancement** (Next)
- Advanced analytics dashboard
- Automated compliance reporting
- Multi-tenant architecture
- Global artifact distribution

### **Phase 3: Monetization** (Future)
- Artifact marketplace
- Usage-based billing
- IP licensing system
- Enterprise SLA management

---

## 🏛️ **Constitutional Declaration**

*This BHIV Bucket system is hereby established as the foundational Truth Engine for AI operations. The constitutional rules defined herein are immutable and shall govern all data operations. The Data Sovereign maintains ultimate authority over this system, with clear escalation procedures for all governance decisions.*

*By using this system, all parties acknowledge and agree to abide by the constitutional framework and authority hierarchy established herein.*

**Version**: 1.0.0  
**Constitutional Hash**: Immutable  
**Authority**: Data Sovereign (Ashmit Pandey)  
**Status**: ✅ Production Ready

---

*BHIV Central Depository - Where AI meets Constitutional Data Governance* 🏛️