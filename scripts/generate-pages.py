#!/usr/bin/env python3
"""
LAB Product Validation Workflow - Pages Generator
Generates role-specific pages with appropriate access controls and functionality
"""

import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import sys
from datetime import datetime

def load_config(config_path):
    """Load configuration from YAML file with fallback"""
    try:
        # Try the specified path first
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        
        # Try alternative paths
        alternative_paths = [
            Path("config/lab-workflow-config.yaml"),
            Path("config/domain-model-config.yaml"),
            Path("../config/lab-workflow-config.yaml")
        ]
        
        for alt_path in alternative_paths:
            if alt_path.exists():
                print(f"📁 Using configuration from: {alt_path}")
                with open(alt_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
        
        # If no config found, provide default pages
        print("⚠️ No configuration file found, using default pages")
        return get_default_pages_config()
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None

def get_default_pages_config():
    """Return default pages configuration"""
    return {
        'pages': [
            {
                'name': 'WorkflowAdminCenter',
                'type': 'admin_dashboard',
                'description': 'Central administration hub for workflow management',
                'security_roles': ['LABAdmin'],
                'layout': 'Dashboard',
                'components': [
                    {'type': 'DataGrid', 'entity': 'System.Workflow', 'title': 'All Workflows'},
                    {'type': 'DataGrid', 'entity': 'System.WorkflowUserTask', 'title': 'All Tasks'},
                    {'type': 'ActionButton', 'action': 'ACT_AssignTask', 'title': 'Reassign Task'},
                    {'type': 'Chart', 'data': 'WorkflowMetrics', 'title': 'Workflow Performance'}
                ]
            },
            {
                'name': 'TaskInbox',
                'type': 'user_dashboard',
                'description': 'Personal task management interface for users',
                'security_roles': ['LABTechnician'],
                'layout': 'TaskManagement',
                'components': [
                    {'type': 'DataGrid', 'entity': 'System.WorkflowUserTask', 'title': 'My Tasks', 'constraint': '[AssignedTo = $currentUser]'},
                    {'type': 'ActionButton', 'action': 'ACT_CompleteTask', 'title': 'Complete Task'},
                    {'type': 'FormView', 'entity': 'ProductValidation', 'title': 'Task Details'}
                ]
            },
            {
                'name': 'TaskDashboard',
                'type': 'user_dashboard',
                'description': 'Personal performance metrics and task history',
                'security_roles': ['LABTechnician'],
                'layout': 'Dashboard',
                'components': [
                    {'type': 'Chart', 'data': 'MyTaskMetrics', 'title': 'My Performance'},
                    {'type': 'DataGrid', 'entity': 'System.WorkflowEndedUserTask', 'title': 'Completed Tasks', 'constraint': '[CompletedBy = $currentUser]'},
                    {'type': 'StatCard', 'metric': 'TasksCompleted', 'title': 'Tasks Completed This Week'}
                ]
            },
            {
                'name': 'PublicDashboard',
                'type': 'viewer_dashboard',
                'description': 'Read-only dashboard for public workflow information',
                'security_roles': ['LABViewer'],
                'layout': 'ReadOnlyDashboard',
                'components': [
                    {'type': 'Chart', 'data': 'PublicWorkflowMetrics', 'title': 'Workflow Statistics'},
                    {'type': 'DataGrid', 'entity': 'ValidationReport', 'title': 'Public Reports', 'constraint': '[IsPublic = true]'},
                    {'type': 'StatCard', 'metric': 'TotalWorkflows', 'title': 'Total Workflows'}
                ]
            },
            {
                'name': 'ImageAcquisitionTask',
                'type': 'task_page',
                'description': 'Specialized page for image capture and quality validation',
                'security_roles': ['LABTechnician'],
                'layout': 'TaskForm',
                'components': [
                    {'type': 'ImageUploader', 'entity': 'ImageAcquisition', 'field': 'ImageFile', 'title': 'Upload Image'},
                    {'type': 'FormView', 'entity': 'ImageAcquisition', 'title': 'Image Details'},
                    {'type': 'ActionButton', 'action': 'ACT_ProcessImageQuality', 'title': 'Validate Quality'},
                    {'type': 'ConditionalView', 'condition': 'IsQualityApproved', 'title': 'Quality Status'}
                ]
            },
            {
                'name': 'DetailedImageAcquisitionTask',
                'type': 'task_page',
                'description': 'Enhanced image processing and analysis interface',
                'security_roles': ['LABTechnician'],
                'layout': 'TaskForm',
                'components': [
                    {'type': 'ImageViewer', 'entity': 'DetailedImageAcquisition', 'field': 'EnhancedImageFile', 'title': 'Enhanced Image'},
                    {'type': 'FormView', 'entity': 'DetailedImageAcquisition', 'title': 'Processing Details'},
                    {'type': 'TextArea', 'field': 'ProcessingNotes', 'title': 'Processing Notes'},
                    {'type': 'ActionButton', 'action': 'ACT_CompleteTask', 'title': 'Complete Processing'}
                ]
            },
            {
                'name': 'ValidationResultPage',
                'type': 'task_page',
                'description': 'Final validation decision interface',
                'security_roles': ['LABAdmin'],
                'layout': 'ValidationForm',
                'components': [
                    {'type': 'FormView', 'entity': 'ValidationResult', 'title': 'Validation Decision'},
                    {'type': 'DropDown', 'field': 'Result', 'enumeration': 'ValidationOutcome', 'title': 'Final Decision'},
                    {'type': 'TextArea', 'field': 'Comments', 'title': 'Validation Comments'},
                    {'type': 'ActionButton', 'action': 'ACT_ValidateWorkflowOutcome', 'title': 'Submit Decision'}
                ]
            },
            {
                'name': 'ReportGenerationPage',
                'type': 'report_page',
                'description': 'Comprehensive report generation and viewing',
                'security_roles': ['LABAdmin', 'LABTechnician', 'LABViewer'],
                'layout': 'ReportLayout',
                'components': [
                    {'type': 'FormView', 'entity': 'ValidationReport', 'title': 'Report Configuration'},
                    {'type': 'DropDown', 'field': 'ReportFormat', 'enumeration': 'ReportFormat', 'title': 'Report Format'},
                    {'type': 'ActionButton', 'action': 'ACT_GenerateValidationReport', 'title': 'Generate Report'},
                    {'type': 'FileDownloader', 'field': 'ReportFile', 'title': 'Download Report'}
                ]
            },
            {
                'name': 'AuditTrailViewer',
                'type': 'admin_page',
                'description': 'Complete audit trail viewer for compliance tracking',
                'security_roles': ['LABAdmin'],
                'layout': 'AuditLayout',
                'components': [
                    {'type': 'DataGrid', 'entity': 'WorkflowAuditTrail', 'title': 'Audit Trail'},
                    {'type': 'SearchBox', 'target': 'AuditTrail', 'title': 'Search Actions'},
                    {'type': 'DatePicker', 'field': 'ActionDate', 'title': 'Filter by Date'},
                    {'type': 'ExportButton', 'data': 'AuditTrail', 'title': 'Export Audit Log'}
                ]
            },
            {
                'name': 'UserManagement',
                'type': 'admin_page',
                'description': 'User and role management interface',
                'security_roles': ['LABAdmin'],
                'layout': 'UserManagement',
                'components': [
                    {'type': 'DataGrid', 'entity': 'Administration.Account', 'title': 'Users'},
                    {'type': 'FormView', 'entity': 'Administration.Account', 'title': 'User Details'},
                    {'type': 'RoleSelector', 'field': 'UserRoles', 'title': 'Assign Roles'},
                    {'type': 'ActionButton', 'action': 'ACT_UpdateUserRoles', 'title': 'Update Roles'}
                ]
            }
        ]
    }

def generate_page_xml(page_config):
    """Generate XML for a single page"""
    try:
        # Create root page element
        page = ET.Element("page")
        page.set("name", page_config.get('name', 'UnknownPage'))
        page.set("type", page_config.get('type', 'page'))
        
        # Add documentation
        if 'description' in page_config:
            documentation = ET.SubElement(page, "documentation")
            documentation.text = page_config['description']
        
        # Add security settings
        if 'security_roles' in page_config:
            security_elem = ET.SubElement(page, "security")
            for role in page_config['security_roles']:
                role_elem = ET.SubElement(security_elem, "allowedRole")
                role_elem.set("name", role)
        
        # Add layout
        if 'layout' in page_config:
            layout_elem = ET.SubElement(page, "layout")
            layout_elem.set("type", page_config['layout'])
        
        # Add components
        if 'components' in page_config and page_config['components']:
            components_elem = ET.SubElement(page, "components")
            
            for component in page_config['components']:
                comp_elem = ET.SubElement(components_elem, "component")
                comp_elem.set("type", component.get('type', 'Unknown'))
                comp_elem.set("title", component.get('title', 'Untitled'))
                
                # Add component-specific attributes
                if 'entity' in component:
                    comp_elem.set("entity", component['entity'])
                if 'field' in component:
                    comp_elem.set("field", component['field'])
                if 'action' in component:
                    comp_elem.set("action", component['action'])
                if 'constraint' in component:
                    comp_elem.set("constraint", component['constraint'])
                if 'enumeration' in component:
                    comp_elem.set("enumeration", component['enumeration'])
        
        return page
        
    except Exception as e:
        print(f"❌ Error creating page XML for {page_config.get('name', 'unknown')}: {e}")
        return None

def create_mendix_xml_header():
    """Create proper Mendix XML header"""
    return '<?xml version="1.0" encoding="UTF-8"?>\n'

def format_xml_output(element):
    """Format XML with proper indentation"""
    from xml.dom import minidom
    rough_string = ET.tostring(element, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ").split('\n', 1)[1]  # Remove first line

def main():
    """Main function to generate pages"""
    parser = argparse.ArgumentParser(description='Generate LAB Workflow Pages')
    parser.add_argument('--config', default='config/lab-workflow-config.yaml', 
                       help='Path to configuration file')
    parser.add_argument('--output', default='output/pages', 
                       help='Output directory for generated files')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    print("📄 Generating LAB Workflow Pages...")
    print(f"📋 Configuration: {args.config}")
    print(f"📁 Output: {args.output}")
    
    if args.debug:
        print(f"🐛 Debug mode enabled")
        print(f"🐛 Python path: {sys.executable}")
        print(f"🐛 Working directory: {Path.cwd()}")
    
    # Create output directory
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created output directory: {output_path.absolute()}")
    
    # Load configuration
    config = load_config(args.config)
    if config is None:
        print("❌ Failed to load configuration")
        return 1
    
    if args.debug:
        print(f"🐛 Loaded configuration keys: {list(config.keys())}")
    
    # Generate pages
    if 'pages' in config and config['pages']:
        print(f"📄 Found {len(config['pages'])} pages to generate")
        
        generated_count = 0
        for page_config in config['pages']:
            try:
                page_name = page_config.get('name', 'Unknown')
                print(f"🔨 Generating: {page_name}")
                
                # Create page XML
                page_xml = generate_page_xml(page_config)
                if page_xml is not None:
                    # Save to file with proper formatting
                    page_file = output_path / f"{page_name}.xml"
                    
                    with open(page_file, 'w', encoding='utf-8') as f:
                        f.write(create_mendix_xml_header())
                        f.write(format_xml_output(page_xml))
                    
                    print(f"✅ Generated: {page_name}.xml")
                    generated_count += 1
                else:
                    print(f"❌ Failed to generate XML for {page_name}")
                    
            except Exception as e:
                print(f"❌ Error generating {page_config.get('name', 'unknown')}: {e}")
                if args.debug:
                    import traceback
                    traceback.print_exc()
        
        print(f"📈 Successfully generated {generated_count} pages")
    else:
        print("⚠️ No pages found in configuration")
    
    print("🎉 Pages generation completed!")
    print(f"📁 Files saved to: {output_path.absolute()}")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)