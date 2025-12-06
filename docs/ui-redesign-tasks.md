# Task Checklist: Modular Research Dashboard & Company Analysis

## Phase 1: Company Analysis Backend Foundation
- [ ] Create `backend/models/company.py` with SQLAlchemy model
- [ ] Create `backend/repositories/company_repository.py` with CRUD methods
- [ ] Update `backend/content_service.py` with `generate_company_analysis` method
- [ ] Update `backend/database.py` imports to include new model
- [ ] Run database migration (create tables)

## Phase 2: Backend API & Integration
- [ ] Update `backend/schemas.py` with Request/Response models
- [ ] Add `POST /api/research/company` endpoint in `backend/main.py`
- [ ] Add `GET /api/history/company` endpoint (or update existing)
- [ ] Create `backend/test_company_analysis.py`
- [ ] Verify API with automated tests

## Phase 3: Frontend Architecture
- [ ] Create `frontend/styles/variables.css` with new design tokens
- [ ] Create `frontend/modules/module-registry.js`
- [ ] Create `frontend/components/research-card.js`
- [ ] Create `frontend/components/output-panel.js`
- [ ] Create `frontend/styles/components.css`

## Phase 4: Dashboard & Module Implementation
- [ ] Implement `frontend/modules/person-research.js` (Migration)
- [ ] Implement `frontend/modules/company-research.js` (New)
- [ ] Refactor `frontend/index.html` to use dynamic containers
- [ ] Refactor `frontend/app.js` to initialize Registry and Modules
- [ ] Integrate Company Search API with frontend

## Phase 5: Polish & Documentation
- [ ] Add `frontend/modules/market-research.js` placeholder
- [ ] Implement CSS animations for transitions
- [ ] Update documentation
- [ ] Create Walkthrough artifact
