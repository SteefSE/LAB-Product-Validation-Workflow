#!/usr/bin/env python3
"""
LAB Product Validation Workflow - Security Generator
FIXED VERSION - Compatible with Mendix 10.18.1 and Workflow Commons 3.12.1
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime

def load_config(config_path):
    """Load configuration from YAML file with proper error handling"""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML config: {e}")
        sys.exit(1)

def generate_module_role_xml(role_name, description, entity_access, page_access, microflow_access):
    """Generate XML for a module role compatible with Mendix 10.18.1"""
    
    # Generate entity access rules
    entity_rules_xml = ""
    for entity, access in entity_access.items():
        if isinstance(access, dict):
            access_type = access.get('access', 'R')
            xpath = access.get('xpath', '')
            xpath_xml = f'<xPathConstraint>{xpath}</xPathConstraint>' if xpath else ''
        else:
            access_type = access
            xpath_xml = ''
        
        entity_rules_xml += f"""
        <entityAccess entity="{entity}" access="{access_type}">
            {xpath_xml}
        </entityAccess>"""
    
    # Generate page access rules
    page_rules_xml = ""
    for page in page_access:
        page_rules_xml += f"""
        <pageAccess page="{page}" access="Full"/>"""
    
    # Generate microflow access rules
    microflow_rules_xml = ""
    for microflow in microflow_access:
        microflow_rules_xml += f"""
        <microflowAccess microflow="{microflow}" access="Full"/>"""
    
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<moduleRole xmlns="http://www.mendix.com/metamodel/Projects/7.0.0" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
            name="{role_name}">
    <documentation>{description} - Compatible with Mendix 10.18.1</documentation>
    <entityAccessRules>{entity_rules_xml}
    </entityAccessRules>
    <pageAccessRules>{page_rules_xml}
    </pageAccessRules>
    <microflowAccessRules>{microflow_rules_xml}
    </microflowAccessRules>
</moduleRole>"""
    
    return xml_content

def main():
    parser = argparse.ArgumentParser(description="Generate LAB Workflow Security Roles")
    parser.add_argument("--config", required=True, help="Path to configuration file")
    parser.add_argument("--output", default="output", help="Output directory")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    security_dir = output_dir / "security"
    security_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔒 Generating LAB Workflow Security Roles...")
    print(f"📁 Output directory: {security_dir}")
    
    # Define security roles compatible with Mendix 10.18.1
    security_roles = [
        {
            "name": "LABAdmin",
            "description": "Full system administration and workflow management capabilities",
            "entity_access": {
                "ProductValidation": "CRUD",
                "ImageAcquisition": "CRUD", 
                "ImageQualityValidation": "CRUD",
                "DetailedImageAcquisition": "CRUD",
                "ImageAnalysis": "CRUD",
                "KPIExtraction": "CRUD",
                "ValidationResult": "CRUD",
                "ValidationReport": "CRUD",
                "WorkflowAuditTrail": "CRUD",
                "System.WorkflowUserTask": "CRUD",
                "System.Workflow": "CRUD",
                "Administration.Account": "R"
            },
            "page_access": [
                "WorkflowAdminCenter",
                "WorkflowAdminDashboard", 
                "TaskAssignment_Management",
                "UserManagement_Workflow",
                "SystemConfiguration",
                "AuditTrailViewer",
                "TaskInbox",
                "ValidationResultPage",
                "ReportGenerationPage"
            ],
            "microflow_access": [
                "ACT_CreateTask",
                "ACT_AssignTask", 
                "ACT_CompleteTask",
                "SUB_CheckUserPermissions",
                "ACT_ProcessImageQuality",
                "DS_GetMyTasks",
                "ACT_InitiateWorkflow",
                "ACT_GenerateValidationReport",
                "ACT_UpdateAuditTrail",
                "ACT_ValidateWorkflowOutcome",
                "SUB_NotifyStakeholders",
                "DS_GetWorkflowHistory",
                "ACT_HandleWorkflowException",
                "SUB_CalculateQualityMetrics",
                "ACT_ArchiveCompletedWorkflow"
            ]
        },
        {
            "name": "LABTechnician", 
            "description": "Task execution and data entry for assigned laboratory workflows",
            "entity_access": {
                "ProductValidation": "R",
                "ImageAcquisition": {
                    "access": "CRUD",
                    "xpath": "[TechnicianID = '[%CurrentUser%]']"
                },
                "ImageQualityValidation": {
                    "access": "CRUD", 
                    "xpath": "[ValidatedBy = '[%CurrentUser%]']"
                },
                "DetailedImageAcquisition": {
                    "access": "CRUD",
                    "xpath": "[TechnicianID = '[%CurrentUser%]']"
                },
                "ImageAnalysis": {
                    "access": "CRUD",
                    "xpath": "[ProcessedBy = '[%CurrentUser%]']"
                },
                "KPIExtraction": {
                    "access": "CRUD",
                    "xpath": "[ExtractedBy = '[%CurrentUser%]']"
                },
                "ValidationResult": "R",
                "ValidationReport": "R",
                "WorkflowAuditTrail": {
                    "access": "R",
                    "xpath": "[PerformedBy = '[%CurrentUser%]']"
                },
                "System.WorkflowUserTask": {
                    "access": "RU",
                    "xpath": "[System.WorkflowUserTask_Account = '[%CurrentUser%]']"
                },
                "System.Workflow": "R",
                "Administration.Account": "R"
            },
            "page_access": [
                "TaskInbox",
                "TaskDashboard", 
                "ImageAcquisitionTask",
                "ImageQualityValidationTask",
                "DetailedImageAcquisitionTask",
                "ImageAnalysisTask",
                "KPIExtractionTask",
                "ReportGenerationPage"
            ],
            "microflow_access": [
                "ACT_CompleteTask",
                "SUB_CheckUserPermissions",
                "ACT_ProcessImageQuality",
                "DS_GetMyTasks",
                "ACT_InitiateWorkflow",
                "ACT_GenerateValidationReport",
                "ACT_UpdateAuditTrail",
                "SUB_NotifyStakeholders",
                "SUB_CalculateQualityMetrics"
            ]
        },
        {
            "name": "LABViewer",
            "description": "Read-only access to completed workflows and public reports",
            "entity_access": {
                "ProductValidation": {
                    "access": "R",
                    "xpath": "[Status = 'Completed']"
                },
                "ImageAcquisition": {
                    "access": "R", 
                    "xpath": "[ProductValidation/Status = 'Completed']"
                },
                "ImageQualityValidation": {
                    "access": "R",
                    "xpath": "[ImageAcquisition/ProductValidation/Status = 'Completed']"
                },
                "DetailedImageAcquisition": {
                    "access": "R",
                    "xpath": "[ProductValidation/Status = 'Completed']"
                },
                "ImageAnalysis": {
                    "access": "R",
                    "xpath": "[ProductValidation/Status = 'Completed']"
                },
                "KPIExtraction": {
                    "access": "R",
                    "xpath": "[ProductValidation/Status = 'Completed']"
                },
                "ValidationResult": "R",
                "ValidationReport": "R",
                "WorkflowAuditTrail": {
                    "access": "R",
                    "xpath": "[ProductValidation/Status = 'Completed']"
                },
                "System.WorkflowUserTask": {
                    "access": "R",
                    "xpath": "[System.Workflow/System.Workflow_ProductValidation/Status = 'Completed']"
                },
                "System.Workflow": {
                    "access": "R",
                    "xpath": "[System.Workflow_ProductValidation/Status = 'Completed']"
                },
                "Administration.Account": "R"
            },
            "page_access": [
                "PublicReportViewer",
                "WorkflowStatusViewer", 
                "ValidationResultViewer",
                "CompletedWorkflowsOverview"
            ],
            "microflow_access": [
                "SUB_CheckUserPermissions",
                "DS_GetWorkflowHistory"
            ]
        }
    ]
    
    # Generate security role XML files
    for role in security_roles:
        xml_content = generate_module_role_xml(
            role["name"],
            role["description"],
            role["entity_access"],
            role["page_access"], 
            role["microflow_access"]
        )
        
        role_file = security_dir / f"{role['name']}.xml"
        with open(role_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"✅ Generated security role: {role['name']}.xml")
    
    print(f"\n🎉 Security roles generation completed!")
    print(f"🔒 Generated {len(security_roles)} security roles")
    print(f"📁 Files saved to: {security_dir}")
    
    # Generate security summary
    summary_file = security_dir / "SECURITY_SUMMARY.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("LAB Product Validation Workflow - Security Summary\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Compatible with: Mendix 10.18.1 + Workflow Commons 3.12.1\n\n")
        
        f.write("Security Roles Overview:\n")
        f.write("-" * 30 + "\n")
        for role in security_roles:
            f.write(f"• {role['name']}\n")
            f.write(f"  Description: {role['description']}\n")
            f.write(f"  Entity Access: {len(role['entity_access'])} entities\n")
            f.write(f"  Page Access: {len(role['page_access'])} pages\n")
            f.write(f"  Microflow Access: {len(role['microflow_access'])} microflows\n\n")
        
        f.write("XPath Constraints Applied:\n")
        f.write("-" * 30 + "\n")
        f.write("• LABTechnician: Data filtered by current user ownership\n")
        f.write("• LABViewer: Only completed workflows visible\n")
        f.write("• LABAdmin: Full access to all data\n\n")
        
        f.write("Compatibility Notes:\n")
        f.write("-" * 20 + "\n")
        f.write("• Uses System.WorkflowUserTask (not WorkflowEndedUserTask)\n")
        f.write("• Compatible with Workflow Commons 3.12.1\n")
        f.write("• XPath constraints use [%CurrentUser%] syntax\n")
        f.write("• No View Entities used (Mendix 11+ feature)\n")
    
    print(f"📋 Generated summary: SECURITY_SUMMARY.txt")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)