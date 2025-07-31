#!/usr/bin/env python3
"""
LAB Product Validation Workflow - Security Generator
Generates security roles with proper access controls and XPath constraints
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
            Path("config/security-config.yaml"),
            Path("../config/lab-workflow-config.yaml")
        ]
        
        for alt_path in alternative_paths:
            if alt_path.exists():
                print(f"📁 Using configuration from: {alt_path}")
                with open(alt_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
        
        # If no config found, provide default security configuration
        print("⚠️ No configuration file found, using default security roles")
        return get_default_security_config()
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None

def get_default_security_config():
    """Return default security configuration"""
    return {
        'security_roles': [
            {
                'name': 'LABAdmin',
                'description': 'Full system administration and workflow management',
                'permissions': {
                    'entity_access': {
                        'ProductValidation': 'CRUD',
                        'ImageAcquisition': 'CRUD',
                        'DetailedImageAcquisition': 'CRUD',
                        'ImageAnalysis': 'CRUD',
                        'KPIExtraction': 'CRUD',
                        'ValidationResult': 'CRUD',
                        'ValidationReport': 'CRUD',
                        'WorkflowAuditTrail': 'CRUD',
                        'System.WorkflowUserTask': 'CRUD',
                        'System.Workflow': 'CRUD',
                        'Administration.Account': 'CRUD'
                    },
                    'page_access': [
                        'WorkflowAdminCenter',
                        'TaskInbox',
                        'ValidationResultPage',
                        'AuditTrailViewer',
                        'UserManagement',
                        'ReportGenerationPage'
                    ],
                    'microflow_access': [
                        'ACT_CreateTask',
                        'ACT_AssignTask',
                        'ACT_CompleteTask',
                        'SUB_CheckUserPermissions',
                        'ACT_ProcessImageQuality',
                        'DS_GetMyTasks',
                        'ACT_InitiateWorkflow',
                        'ACT_GenerateValidationReport',
                        'ACT_UpdateAuditTrail',
                        'ACT_ValidateWorkflowOutcome'
                    ]
                }
            },
            {
                'name': 'LABTechnician',
                'description': 'Task execution and data entry for assigned workflows',
                'permissions': {
                    'entity_access': {
                        'ProductValidation': {
                            'access': 'R',
                            'xpath': None
                        },
                        'ImageAcquisition': {
                            'access': 'CRUD',
                            'xpath': '[TechnicianID = $currentUser/Name]'
                        },
                        'DetailedImageAcquisition': {
                            'access': 'CRUD',
                            'xpath': '[ProcessedBy = $currentUser/Name]'
                        },
                        'ImageAnalysis': {
                            'access': 'CRUD',
                            'xpath': '[ProcessedBy = $currentUser/Name]'
                        },
                        'KPIExtraction': {
                            'access': 'CRUD',
                            'xpath': '[ExtractedBy = $currentUser/Name]'
                        },
                        'ValidationResult': 'R',
                        'ValidationReport': 'R',
                        'WorkflowAuditTrail': {
                            'access': 'R',
                            'xpath': '[PerformedBy = $currentUser/Name]'
                        },
                        'System.WorkflowUserTask': {
                            'access': 'RU',
                            'xpath': '[System.WorkflowUserTask_Account = $currentUser]'
                        }
                    },
                    'page_access': [
                        'TaskInbox',
                        'TaskDashboard',
                        'ImageAcquisitionTask',
                        'DetailedImageAcquisitionTask',
                        'ReportGenerationPage'
                    ],
                    'microflow_access': [
                        'ACT_CompleteTask',
                        'SUB_CheckUserPermissions',
                        'ACT_ProcessImageQuality',
                        'DS_GetMyTasks',
                        'ACT_InitiateWorkflow',
                        'ACT_GenerateValidationReport',
                        'ACT_UpdateAuditTrail'
                    ]
                }
            },
            {
                'name': 'LABViewer',
                'description': 'Read-only access to public workflow information',
                'permissions': {
                    'entity_access': {
                        'ProductValidation': {
                            'access': 'R',
                            'xpath': '[IsPublic = true]'
                        },
                        'ValidationResult': {
                            'access': 'R',
                            'xpath': '[IsPublic = true]'
                        },
                        'ValidationReport': {
                            'access': 'R',
                            'xpath': '[IsPublic = true]'
                        },
                        'WorkflowAuditTrail': {
                            'access': 'R',
                            'xpath': '[IsPublic = true]'
                        },
                        'System.Workflow': {
                            'access': 'R',
                            'xpath': '[IsPublic = true]'
                        }
                    },
                    'page_access': [
                        'PublicDashboard',
                        'ReportGenerationPage'
                    ],
                    'microflow_access': [
                        'SUB_CheckUserPermissions',
                        'ACT_GenerateValidationReport'
                    ]
                }
            }
        ]
    }

def generate_security_role_xml(role_config):
    """Generate XML for a single security role"""
    try:
        # Create root security role element
        role = ET.Element("userRole")
        role.set("name", role_config.get('name', 'UnknownRole'))
        
        # Add documentation
        if 'description' in role_config:
            documentation = ET.SubElement(role, "documentation")
            documentation.text = role_config['description']
        
        # Add permissions
        if 'permissions' in role_config:
            permissions = role_config['permissions']
            
            # Entity access permissions
            if 'entity_access' in permissions:
                entity_access = ET.SubElement(role, "entityAccess")
                
                for entity_name, access_config in permissions['entity_access'].items():
                    entity_elem = ET.SubElement(entity_access, "entity")
                    entity_elem.set("name", entity_name)
                    
                    if isinstance(access_config, str):
                        # Simple access level
                        entity_elem.set("access", access_config)
                    elif isinstance(access_config, dict):
                        # Complex access with XPath
                        entity_elem.set("access", access_config.get('access', 'R'))
                        if access_config.get('xpath'):
                            xpath_elem = ET.SubElement(entity_elem, "xpath")
                            xpath_elem.text = access_config['xpath']
            
            # Page access permissions
            if 'page_access' in permissions:
                page_access = ET.SubElement(role, "pageAccess")
                
                for page_name in permissions['page_access']:
                    page_elem = ET.SubElement(page_access, "page")
                    page_elem.set("name", page_name)
            
            # Microflow access permissions
            if 'microflow_access' in permissions:
                microflow_access = ET.SubElement(role, "microflowAccess")
                
                for microflow_name in permissions['microflow_access']:
                    microflow_elem = ET.SubElement(microflow_access, "microflow")
                    microflow_elem.set("name", microflow_name)
        
        return role
        
    except Exception as e:
        print(f"❌ Error creating security role XML for {role_config.get('name', 'unknown')}: {e}")
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

def create_security_summary(roles_config):
    """Create a markdown summary of security configuration"""
    summary = """# LAB Workflow Security Configuration Summary

Generated on: {timestamp}

## Security Roles Overview

""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    for role in roles_config:
        summary += f"### 🔐 {role['name']}\n\n"
        summary += f"**Description:** {role.get('description', 'No description')}\n\n"
        
        if 'permissions' in role:
            permissions = role['permissions']
            
            # Entity access
            if 'entity_access' in permissions:
                summary += "**Entity Access:**\n"
                for entity, access in permissions['entity_access'].items():
                    if isinstance(access, str):
                        summary += f"- {entity}: {access}\n"
                    else:
                        summary += f"- {entity}: {access.get('access', 'R')}"
                        if access.get('xpath'):
                            summary += f" (XPath: `{access['xpath']}`)"
                        summary += "\n"
                summary += "\n"
            
            # Page access
            if 'page_access' in permissions:
                summary += "**Page Access:**\n"
                for page in permissions['page_access']:
                    summary += f"- {page}\n"
                summary += "\n"
            
            # Microflow access
            if 'microflow_access' in permissions:
                summary += "**Microflow Access:**\n"
                for microflow in permissions['microflow_access']:
                    summary += f"- {microflow}\n"
                summary += "\n"
        
        summary += "---\n\n"
    
    return summary

def main():
    """Main function to generate security roles"""
    parser = argparse.ArgumentParser(description='Generate LAB Workflow Security Roles')
    parser.add_argument('--config', default='config/lab-workflow-config.yaml', 
                       help='Path to configuration file')
    parser.add_argument('--output', default='output/security', 
                       help='Output directory for generated files')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    print("🔐 Generating LAB Workflow Security Roles...")
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
    
    # Generate security roles
    if 'security_roles' in config and config['security_roles']:
        print(f"🔐 Found {len(config['security_roles'])} security roles to generate")
        
        generated_count = 0
        for role_config in config['security_roles']:
            try:
                role_name = role_config.get('name', 'Unknown')
                print(f"🔨 Generating: {role_name}")
                
                # Create security role XML
                role_xml = generate_security_role_xml(role_config)
                if role_xml is not None:
                    # Save to file with proper formatting
                    role_file = output_path / f"{role_name}.xml"
                    
                    with open(role_file, 'w', encoding='utf-8') as f:
                        f.write(create_mendix_xml_header())
                        f.write(format_xml_output(role_xml))
                    
                    print(f"✅ Generated: {role_name}.xml")
                    generated_count += 1
                else:
                    print(f"❌ Failed to generate XML for {role_name}")
                    
            except Exception as e:
                print(f"❌ Error generating {role_config.get('name', 'unknown')}: {e}")
                if args.debug:
                    import traceback
                    traceback.print_exc()
        
        # Generate security summary
        summary = create_security_summary(config['security_roles'])
        summary_file = output_path / "SECURITY_SUMMARY.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"📋 Generated security summary: SECURITY_SUMMARY.md")
        
        print(f"📈 Successfully generated {generated_count} security roles")
    else:
        print("⚠️ No security roles found in configuration")
    
    print("🎉 Security roles generation completed!")
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