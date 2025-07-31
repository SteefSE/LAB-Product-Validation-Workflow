#!/usr/bin/env python3
"""
LAB Product Validation Workflow - Microflows Generator
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

def generate_microflow_xml(name, description, parameters=None, return_type="Boolean", security_roles=None):
    """Generate XML for a microflow compatible with Mendix 10.18.1"""
    
    parameters = parameters or []
    security_roles = security_roles or ["LABAdmin", "LABTechnician"]
    
    # Generate parameters XML
    params_xml = ""
    for param in parameters:
        param_name = param.get('name', 'Parameter')
        param_type = param.get('type', 'String')
        params_xml += f"""
        <parameter name="{param_name}" type="{param_type}"/>"""
    
    # Generate security roles XML
    roles_xml = ""
    for role in security_roles:
        roles_xml += f"""
        <allowedRole name="{role}"/>"""
    
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<microflow xmlns="http://www.mendix.com/metamodel/MicroFlows/7.0.0" 
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
           name="{name}">
    <documentation>{description} - Compatible with Mendix 10.18.1</documentation>
    <objectCollection>
        <startEvent>
            <position x="100" y="100"/>
            <size width="20" height="20"/>
        </startEvent>
        <actionActivity name="ProcessAction">
            <position x="200" y="100"/>
            <size width="120" height="60"/>
            <action type="CreateObject">
                <documentation>Main processing logic for {name}</documentation>
            </action>
        </actionActivity>
        <endEvent>
            <position x="400" y="100"/>
            <size width="20" height="20"/>
            <returnValue>{return_type.lower()}</returnValue>
        </endEvent>
    </objectCollection>
    <flows>
        <sequenceFlow>
            <origin>startEvent</origin>
            <destination>ProcessAction</destination>
        </sequenceFlow>
        <sequenceFlow>
            <origin>ProcessAction</origin>
            <destination>endEvent</destination>
        </sequenceFlow>
    </flows>
    <parameters>{params_xml}
    </parameters>
    <returnType>{return_type}</returnType>
    <allowedRoles>{roles_xml}
    </allowedRoles>
</microflow>"""
    
    return xml_content

def main():
    parser = argparse.ArgumentParser(description="Generate LAB Workflow Microflows")
    parser.add_argument("--config", required=True, help="Path to configuration file")
    parser.add_argument("--output", default="output", help="Output directory")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    microflows_dir = output_dir / "microflows"
    microflows_dir.mkdir(parents=True, exist_ok=True)
    
    print("⚡ Generating LAB Workflow Microflows...")
    print(f"📁 Output directory: {microflows_dir}")
    
    # Define microflows compatible with Mendix 10.18.1
    microflows = [
        {
            "name": "ACT_CreateTask",
            "description": "Creates new workflow task with proper assignment and initial status",
            "parameters": [
                {"name": "TaskTitle", "type": "String"},
                {"name": "AssignedUser", "type": "Administration.Account"},
                {"name": "WorkflowContext", "type": "ProductValidation"}
            ],
            "return_type": "System.WorkflowUserTask",
            "security_roles": ["LABAdmin", "LABTechnician"]
        },
        {
            "name": "ACT_AssignTask",
            "description": "Assigns tasks to users based on role and current workload",
            "parameters": [
                {"name": "Task", "type": "System.WorkflowUserTask"},
                {"name": "NewAssignee", "type": "Administration.Account"}
            ],
            "return_type": "Boolean",
            "security_roles": ["LABAdmin"]
        },
        {
            "name": "ACT_CompleteTask",
            "description": "Marks task as completed and triggers workflow progression",
            "parameters": [
                {"name": "Task", "type": "System.WorkflowUserTask"},
                {"name": "CompletionData", "type": "String"}
            ],
            "return_type": "Boolean",
            "security_roles": ["LABAdmin", "LABTechnician"]
        },
        {
            "name": "SUB_CheckUserPermissions",
            "description": "Validates user access rights for specific workflow actions",
            "parameters": [
                {"name": "User", "type": "Administration.Account"},
                {"name": "RequiredRole", "type": "String"},
                {"name": "EntityToAccess", "type": "String"}
            ],
            "return_type": "Boolean",
            "security_roles": ["LABAdmin", "LABTechnician", "LABViewer"]
        },
        {
            "name": "ACT_ProcessImageQuality",
            "description": "Validates image quality and determines approval status for workflow progression",
            "parameters": [
                {"name": "ImageAcquisition", "type": "ImageAcquisition"},
                {"name": "QualityThreshold", "type": "Decimal"}
            ],
            "return_type": "Boolean",
            "security_roles": ["LABAdmin", "LABTechnician"]
        },
        {
            "name": "DS_GetMyTasks",
            "description": "Returns tasks filtered by current user with proper XPath constraints",
            "parameters": [
                {"name": "CurrentUser", "type": "Administration.Account"}
            ],
            "return_type": "List",
            "security_roles": ["LABAdmin", "LABTechnician", "LABViewer"]
        },
        {
            "name": "ACT_InitiateWorkflow",
            "description": "Initiates new LAB Product Validation workflow instance",
            "parameters": [
                {"name": "ProductValidation", "type": "ProductValidation"},
                {"name": "InitiatingUser", "type": "Administration.Account"}
            ],
            "return_type": "System.Workflow",
            "security_roles": ["LABAdmin", "LABTechnician"]
        },
        {
            "name": "ACT_GenerateValidationReport",
            "description": "Generates comprehensive validation report with all workflow data",
            "parameters": [
                {"name": "ProductValidation", "type": "ProductValidation"},
                {"name": "ReportFormat", "type": "ReportFormat"}
            ],
            "return_type": "ValidationReport",
            "security_roles": ["LABAdmin", "LABTechnician"]
        },
        {
            "name": "ACT_UpdateAuditTrail",
            "description": "Updates workflow audit trail with action details for compliance",
            "parameters": [
                {"name": "ActionType", "type": "AuditActionType"},
                {"name": "EntityAffected", "type": "String"},
                {"name": "PerformedBy", "type": "Administration.Account"},
                {"name": "ChangeDetails", "type": "String"}
            ],
            "return_type": "WorkflowAuditTrail",
            "security_roles": ["LABAdmin", "LABTechnician"]
        },
        {
            "name": "ACT_ValidateWorkflowOutcome",
            "description": "Validates final workflow outcome and determines TRUE/FALSE result",
            "parameters": [
                {"name": "ProductValidation", "type": "ProductValidation"},
                {"name": "ValidationCriteria", "type": "String"}
            ],
            "return_type": "Boolean",
            "security_roles": ["LABAdmin"]
        },
        {
            "name": "SUB_NotifyStakeholders",
            "description": "Sends notifications to relevant stakeholders based on workflow events",
            "parameters": [
                {"name": "NotificationType", "type": "String"},
                {"name": "Recipients", "type": "String"},
                {"name": "MessageContent", "type": "String"}
            ],
            "return_type": "Boolean",
            "security_roles": ["LABAdmin", "LABTechnician"]
        },
        {
            "name": "DS_GetWorkflowHistory",
            "description": "Retrieves complete workflow history for audit and reporting purposes",
            "parameters": [
                {"name": "ProductValidation", "type": "ProductValidation"}
            ],
            "return_type": "List",
            "security_roles": ["LABAdmin", "LABViewer"]
        },
        {
            "name": "ACT_HandleWorkflowException",
            "description": "Handles workflow exceptions and error conditions gracefully",
            "parameters": [
                {"name": "ExceptionType", "type": "String"},
                {"name": "ErrorContext", "type": "String"},
                {"name": "RecoveryAction", "type": "String"}
            ],
            "return_type": "Boolean",
            "security_roles": ["LABAdmin"]
        },
        {
            "name": "SUB_CalculateQualityMetrics",
            "description": "Calculates quality metrics and performance indicators for workflow steps",
            "parameters": [
                {"name": "ImageAcquisition", "type": "ImageAcquisition"},
                {"name": "AnalysisResults", "type": "String"}
            ],
            "return_type": "Decimal",
            "security_roles": ["LABAdmin", "LABTechnician"]
        },
        {
            "name": "ACT_ArchiveCompletedWorkflow",
            "description": "Archives completed workflow data for long-term storage and compliance",
            "parameters": [
                {"name": "ProductValidation", "type": "ProductValidation"},
                {"name": "ArchiveLocation", "type": "String"}
            ],
            "return_type": "Boolean",
            "security_roles": ["LABAdmin"]
        }
    ]
    
    # Generate microflow XML files
    for microflow in microflows:
        xml_content = generate_microflow_xml(
            microflow["name"],
            microflow["description"], 
            microflow.get("parameters", []),
            microflow.get("return_type", "Boolean"),
            microflow.get("security_roles", ["LABAdmin", "LABTechnician"])
        )
        
        microflow_file = microflows_dir / f"{microflow['name']}.xml"
        with open(microflow_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"✅ Generated microflow: {microflow['name']}.xml")
    
    print(f"\n🎉 Microflows generation completed!")
    print(f"⚡ Generated {len(microflows)} microflows")
    print(f"📁 Files saved to: {microflows_dir}")
    
    # Generate microflows summary
    summary_file = microflows_dir / "MICROFLOWS_SUMMARY.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("LAB Product Validation Workflow - Microflows Summary\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Compatible with: Mendix 10.18.1 + Workflow Commons 3.12.1\n\n")
        
        f.write("Generated Microflows:\n")
        f.write("-" * 30 + "\n")
        for microflow in microflows:
            f.write(f"• {microflow['name']}\n")
            f.write(f"  Description: {microflow['description']}\n")
            f.write(f"  Return Type: {microflow.get('return_type', 'Boolean')}\n")
            f.write(f"  Security Roles: {', '.join(microflow.get('security_roles', []))}\n\n")
    
    print(f"📋 Generated summary: MICROFLOWS_SUMMARY.txt")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)