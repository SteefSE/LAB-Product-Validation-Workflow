#!/usr/bin/env python3
"""
LAB Product Validation Workflow - MPK Package Generator
Creates a Mendix Package (MPK) file from generated XML components
"""

import zipfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import sys
from datetime import datetime
import uuid

def create_module_manifest():
    """Create the module manifest for the MPK package"""
    manifest = {
        "name": "LABProductValidationWorkflow",
        "version": "1.0.0",
        "description": "Complete LAB Product Validation Workflow with TRUE/FALSE decision logic",
        "author": "LAB Workflow Generator",
        "mendixVersion": "11.0.0",
        "packageType": "Module",
        "dependencies": [
            {
                "name": "WorkflowCommons",
                "version": "4.0.0"
            },
            {
                "name": "Atlas_Core",
                "version": "3.0.0"
            }
        ],
        "license": "MIT",
        "keywords": ["workflow", "validation", "lab", "quality"],
        "created": datetime.now().isoformat(),
        "guid": str(uuid.uuid4())
    }
    return manifest

def create_module_xml():
    """Create the main module XML structure"""
    module = ET.Element("module")
    module.set("name", "LABProductValidationWorkflow")
    module.set("version", "1.0.0")
    
    # Add documentation
    documentation = ET.SubElement(module, "documentation")
    documentation.text = """
LAB Product Validation Workflow Module

This module provides a complete automation package for LAB product validation workflows
with TRUE/FALSE decision logic, role-based security, and comprehensive audit trails.

Features:
- 8 Domain Model entities with proper associations
- 8 Comprehensive enumerations for workflow stages and outcomes
- 10 Role-specific microflows for workflow operations
- 10 User interface pages for different user roles
- 3 Security roles with XPath constraints
- 1 Complete workflow with TRUE/FALSE decision points

Installation:
1. Import this MPK file into Mendix Studio Pro
2. Install Workflow Commons 4.0+ from App Store
3. Configure user entity in App Settings > Workflows tab
4. Add navigation items for key pages
5. Create test users with appropriate roles

For detailed documentation, see the included README files.
"""
    
    # Add dependencies
    dependencies = ET.SubElement(module, "dependencies")
    
    workflow_commons = ET.SubElement(dependencies, "dependency")
    workflow_commons.set("name", "WorkflowCommons")
    workflow_commons.set("version", "4.0.0")
    
    atlas_core = ET.SubElement(dependencies, "dependency")
    atlas_core.set("name", "Atlas_Core")  
    atlas_core.set("version", "3.0.0")
    
    return module

def create_mpk_package(output_dir, mpk_filename):
    """Create the MPK package from generated XML files"""
    output_path = Path(output_dir)
    mpk_path = output_path / mpk_filename
    
    print(f"📦 Creating MPK package: {mpk_path}")
    
    # Create the MPK file (which is essentially a ZIP file)
    with zipfile.ZipFile(mpk_path, 'w', zipfile.ZIP_DEFLATED) as mpk:
        
        # Add manifest
        manifest = create_module_manifest()
        mpk.writestr("manifest.json", json.dumps(manifest, indent=2))
        print(f"✅ Added manifest.json")
        
        # Add module XML
        module_xml = create_module_xml()
        from xml.dom import minidom
        rough_string = ET.tostring(module_xml, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        formatted_xml = reparsed.toprettyxml(indent="  ")
        mpk.writestr("module.xml", formatted_xml)
        print(f"✅ Added module.xml")
        
        # Add all generated XML files
        base_output = Path("output")
        
        # Enumerations
        enum_dir = base_output / "enumerations"
        if enum_dir.exists():
            for xml_file in enum_dir.glob("*.xml"):
                arc_path = f"enumerations/{xml_file.name}"
                mpk.write(xml_file, arc_path)
                print(f"✅ Added {arc_path}")
        
        # Domain Model
        domain_dir = base_output / "domain-model"
        if domain_dir.exists():
            for xml_file in domain_dir.glob("*.xml"):
                arc_path = f"domain-model/{xml_file.name}"
                mpk.write(xml_file, arc_path)
                print(f"✅ Added {arc_path}")
        
        # Security
        security_dir = base_output / "security"
        if security_dir.exists():
            for xml_file in security_dir.glob("*.xml"):
                arc_path = f"security/{xml_file.name}"
                mpk.write(xml_file, arc_path)
                print(f"✅ Added {arc_path}")
        
        # Microflows
        microflows_dir = base_output / "microflows"
        if microflows_dir.exists():
            for xml_file in microflows_dir.glob("*.xml"):
                arc_path = f"microflows/{xml_file.name}"
                mpk.write(xml_file, arc_path)
                print(f"✅ Added {arc_path}")
        
        # Pages
        pages_dir = base_output / "pages"
        if pages_dir.exists():
            for xml_file in pages_dir.glob("*.xml"):
                arc_path = f"pages/{xml_file.name}"
                mpk.write(xml_file, arc_path)
                print(f"✅ Added {arc_path}")
        
        # Workflows
        workflows_dir = base_output / "workflows"
        if workflows_dir.exists():
            for xml_file in workflows_dir.glob("*.xml"):
                arc_path = f"workflows/{xml_file.name}"
                mpk.write(xml_file, arc_path)
                print(f"✅ Added {arc_path}")
        
        # Add documentation files
        docs_to_include = [
            "output/security/SECURITY_SUMMARY.md",
            "output/enumerations/ENUMERATIONS_SUMMARY.md", 
            "output/workflows/WORKFLOW_DIAGRAM.md",
            "output/PROJECT_SUMMARY.md"
        ]
        
        for doc_path in docs_to_include:
            doc_file = Path(doc_path)
            if doc_file.exists():
                arc_path = f"documentation/{doc_file.name}"
                mpk.writestr(arc_path, doc_file.read_text(encoding='utf-8'))
                print(f"✅ Added {arc_path}")
        
        # Add installation guide
        install_guide = create_installation_guide()
        mpk.writestr("documentation/INSTALLATION_GUIDE.md", install_guide)
        print(f"✅ Added documentation/INSTALLATION_GUIDE.md")
    
    return mpk_path

def create_installation_guide():
    """Create installation guide for the MPK package"""
    return """# LAB Product Validation Workflow - Installation Guide

## 🚀 Quick Installation

### Prerequisites
- Mendix Studio Pro 11+
- Workflow Commons 4.0+ (install from App Store)

### Installation Steps

1. **Import MPK Package**
   - In Studio Pro: File → Import App Package
   - Select this MPK file
   - Choose import location (new module recommended)

2. **Install Dependencies**
   - App Store → Search "Workflow Commons" 
   - Download and install version 4.0+
   - Synchronize all dependencies

3. **Configure Workflow Commons**
   - App Settings → Workflows tab
   - Set User entity to "Administration.Account"

4. **Add Navigation**
   - Add these pages to your navigation:
     - WorkflowAdminCenter (for Administrators)
     - TaskInbox (for Technicians)
     - PublicDashboard (for Viewers)

5. **Create Security Roles**
   - App Security → User roles
   - Create: LABAdmin, LABTechnician, LABViewer
   - Assign appropriate permissions as defined in security XML files

6. **Create Test Users**
   - Create users with different roles for testing
   - Assign appropriate security roles

## 🔧 Post-Installation Configuration

### Microflows
The generated microflows provide structure but need implementation:
- Add business logic to action microflows
- Configure data source microflows with proper XPath
- Implement validation rules

### Pages
The generated pages need customization:
- Adjust layouts and styling
- Configure data sources
- Add proper navigation

### Workflows
The workflow definition needs Studio Pro configuration:
- Open workflow in Studio Pro
- Configure user task assignments
- Set up decision logic
- Test workflow execution

## 📊 Generated Components

- **8 Entities**: Complete domain model with associations
- **8 Enumerations**: Workflow stages, outcomes, formats
- **10 Microflows**: Core workflow operations
- **10 Pages**: Role-based user interfaces
- **3 Security Roles**: Admin, Technician, Viewer
- **1 Workflow**: Complete TRUE/FALSE validation process

## 🎯 Next Steps

1. Test basic functionality
2. Customize UI components
3. Implement business logic
4. Deploy to cloud environment
5. Create end-user documentation

For detailed technical documentation, see the included summary files.
"""

def main():
    """Main function to generate MPK package"""
    parser = argparse.ArgumentParser(description='Generate LAB Workflow MPK Package')
    parser.add_argument('--output', default='output', 
                       help='Output directory containing generated XML files')
    parser.add_argument('--filename', default='LABProductValidationWorkflow_v1.0.0.mpk',
                       help='MPK filename')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    print("📦 Generating LAB Workflow MPK Package...")
    print(f"📁 Source directory: {args.output}")
    print(f"📦 MPK filename: {args.filename}")
    
    # Check if source directories exist
    base_output = Path(args.output)
    if not base_output.exists():
        print(f"❌ Output directory not found: {base_output}")
        print("❌ Please run the project generation first: automation\\generate-project.bat")
        return 1
    
    # Count available files
    total_files = 0
    for subdir in ['enumerations', 'domain-model', 'security', 'microflows', 'pages', 'workflows']:
        subdir_path = base_output / subdir
        if subdir_path.exists():
            xml_files = list(subdir_path.glob('*.xml'))
            total_files += len(xml_files)
            print(f"📊 Found {len(xml_files)} files in {subdir}/")
    
    if total_files == 0:
        print("❌ No XML files found to package")
        print("❌ Please run the project generation first: automation\\generate-project.bat")
        return 1
    
    print(f"📈 Total files to package: {total_files}")
    
    try:
        # Create the MPK package
        mpk_path = create_mpk_package(args.output, args.filename)
        
        # Get file size
        file_size = mpk_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        print("🎉 MPK package generation completed!")
        print(f"📦 Package file: {mpk_path.absolute()}")
        print(f"📏 Package size: {file_size_mb:.2f} MB")
        print(f"📊 Total components: {total_files} XML files")
        
        print("\n🚀 Next Steps:")
        print("1. Open Mendix Studio Pro")
        print("2. File → Import App Package")  
        print(f"3. Select: {mpk_path.absolute()}")
        print("4. Follow the installation guide in the package")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error creating MPK package: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Package generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)