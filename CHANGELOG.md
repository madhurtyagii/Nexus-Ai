All notable changes to Nexus AI will be documented in this file.

## [2.6.0] - 2026-02-19
### Added
- 🌓 **Theme Persistence** - Application now remembers light/dark mode preference across reloads
- 📊 **Redesigned Storage Bar** - Professional indicator with vibrant gradients and soft glow on the Files page
- 🎨 **Premium Off-White Aesthetic** - Comprehensive light mode overhaul for improved visual comfort and high-end feel
- 🧱 **Enhanced Card Depth** - Multi-layered shadows and subtle gradients for a truly premium component experience

### Improved
- Standardized Nexus Intelligence card to match global card aesthetics
- Precise horizontal centering for Floating Refinement Bar via Framer Motion
- Harmonized card styles across Dashboard, Files, Tasks, and Project Detail pages

### Fixed
- "Flashy" light mode sections with hardcoded dark styles
- Conflicting CSS transforms in Floating Refinement Bar
- Missing `Database` icon import in Files.jsx

## [2.2.0] - 2026-02-06
### Added
- 🖱️ **6 Cursor Effects** - Ring, Particles, Ribbon, Aurora, Stardust, Orbit with Settings controls
- 👤 **Account Editing** - Update username & email in Settings with live validation
- 🔒 **PUT /auth/me** - Backend endpoint for profile updates
- 🎨 **Enhanced Settings UI** - Editable fields with pencil icons, save/cancel actions
- 📝 **Updated READMEs** - Comprehensive documentation with new logo

### Improved
- Settings Appearance tab with cursor effect selector
- Account tab with inline editing capabilities
- Username validation to allow spaces and capitals

## [2.1.0] - 2024-05-20
### Added
- Comprehensive Google-style docstrings for all backend modules.
- Detailed JSDoc documentation for all frontend React components.
- New `docs/` directory with Quickstart, User, Agent, and Architecture guides.
- Professional `README.md` with badges and overhauled feature list.
- Enhanced OpenAPI metadata for better developer experience.
- Pydantic schema examples for API endpoints.

### Improved
- Memory system UI and documentation.
- Project wizard documentation.
- Real-time activity monitoring feedback.

### Fixed
- Various minor JSDoc and docstring inconsistencies.
- Metadata synchronization between backend routers and main app.

## [2.0.0] - 2024-04-15
### Added
- Initial release of the multi-agent orchestration engine.
- Project-based planning and execution.
- Semantic memory indexing.
- WebSocket integration for live updates.
