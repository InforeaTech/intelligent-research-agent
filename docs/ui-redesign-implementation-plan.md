# UI Redesign: Modular Research Dashboard + Company Analysis API

## Overview

Transform the current single-purpose research UI into an **extensible, modular dashboard** with a **plugin-like architecture**. Add new **Company Analysis** research type with full backend API support.

This plan follows a **Backend-First** approach: we will establish the data structures, logic, and API endpoints before building the UI that consumes them.

## User Review Required

> [!IMPORTANT]
> **Database Schema**: Company Analysis will create new `companies` table. 

> [!WARNING]  
> **Breaking Change**: The `index.html` structure will be significantly refactored in Phase 4.

---

## Phase Overview

| Phase | Scope | Effort | Dependencies |
|-------|-------|--------|--------------|
| **Phase 1** | Company Analysis Backend | 4h | None |
| **Phase 2** | API Endpoints & Testing | 3h | Phase 1 |
| **Phase 3** | Frontend Architecture | 3h | Phase 2 |
| **Phase 4** | Dashboard & Module Implementation | 4h | Phase 3 |
| **Phase 5** | Polish & Documentation | 2h | Phase 4 |

**Total Estimate**: 16 hours

---

## Phase 1: Company Analysis Backend

### Goals
- Create Database Models (`Company`)
- Create Repository Layer
- Implement Analysis Logic (LLM Prompts)

### Proposed Changes

#### [NEW] `backend/models/company.py`
```python
class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Core Data
    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100))
    website = Column(String(500))
    
    # Analysis Blocks (Text/Markdown)
    overview = Column(Text, nullable=False)
    financials = Column(Text)
    competitors = Column(Text)  # stored as JSON or structured text
    swot_analysis = Column(Text) # stored as JSON or structured text
    
    # Metadata
    search_provider = Column(String(50))
    model_provider = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
```

#### [NEW] `backend/repositories/company_repository.py`
Standard CRUD operations:
- `create(...)`
- `get_by_id(...)`
- `get_recent_by_user(...)`
- `delete(...)`

#### [MODIFY] `backend/content_service.py`
Add `generate_company_analysis` method:
- Prompts optimized for financial/SWOT analysis.
- Structured output parsing.

---

## Phase 2: API Endpoints & Testing

### Goals
- Expose Company Analysis via REST API
- Ensure robust error handling
- Verify with automated tests

### Proposed Changes

#### [MODIFY] `backend/schemas.py`
```python
class CompanyAnalysisRequest(BaseModel):
    company_name: str
    focus_areas: List[str] = ["overview", "financials", "swot"]
    # ... other standard fields

class CompanyAnalysisResponse(BaseModel):
    id: int
    company_name: str
    overview: str
    financials: Optional[str]
    swot: Optional[Dict]
    # ...
```

#### [MODIFY] `backend/main.py`
- `POST /api/research/company`: Trigger analysis
- `GET /api/profiles/company`: List history (rename/consolidate history endpoints?)
- `GET /api/profiles/company/{id}`: Get details

#### Verification
- `pytest backend/test_company_analysis.py`

---

## Phase 3: Frontend Architecture

### Goals
- Establish Modular Registry System
- CSS Variables & Design Tokens (Dark Mode Premium)
- Component Base

### Proposed Changes

#### [NEW] `frontend/styles/variables.css`
Define premium color palette (slate, vibrant accents), spacing, and glassmorphism tokens.

#### [NEW] `frontend/modules/module-registry.js`
The core engine for the new UI:
- `ModuleRegistry` object to manage available research types.

#### [NEW] `frontend/components/`
- `research-card.js`: The dashboard entry point for a module.
- `output-panel.js`: A tabbed interface for displaying results.

---

## Phase 4: Dashboard & Module Implementation

### Goals
- Visual Overhaul of `index.html`
- Implement Modules (Person & Company)
- Integrate with Backend APIs

### Proposed Changes

#### [MODIFY] `frontend/index.html`
- Replace static form with **Category Grid**.
- Add hidden **Dynamic Input Panel**.
- Add **Result/Output Area**.

#### [NEW] `frontend/modules/company-research.js`
Definition for the company module:
- **Inputs**: Company Name, Industry, Focus Areas.
- **Output Tabs**: Overview, Financials, SWOT, Competitors.
- **API**: Calls `POST /api/research/company`.

#### [NEW] `frontend/modules/person-research.js`
Migrate existing logic into a module format.
- **Inputs**: Name, Company, etc.
- **API**: Calls `POST /api/research/profile`.

#### [MODIFY] `frontend/app.js`
- Initialize `ModuleRegistry`.
- Render Dashboard.
- Handle styling transitions between Dashboard -> Input -> Loading -> Results.

---

## Phase 5: Polish & Documentation

### Goals
- Animations (View transitions)
- "Coming Soon" styling for future modules
- Documentation

### Implementation
- Add `frontend/modules/market-research.js` (Placeholder).
- CSS animations for card hover and panel slide-in.
