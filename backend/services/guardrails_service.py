import re
from datetime import datetime
from models import db, GuardrailsConfig, GuardrailsLog
from services.auth_service import AuthService
from config import Config

class GuardrailsService:
    """LangChain middleware for guardrails and content moderation"""
    
    # Default guardrails rules
    DEFAULT_RULES = [
        {
            'rule_type': 'PII_EMAIL',
            'enabled': True,
            'severity': 'high',
            'description': 'Detect email addresses in content',
            'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        },
        {
            'rule_type': 'PII_PHONE',
            'enabled': True,
            'severity': 'high',
            'description': 'Detect phone numbers',
            'pattern': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        },
        {
            'rule_type': 'PII_SSN',
            'enabled': True,
            'severity': 'high',
            'description': 'Detect Social Security Numbers',
            'pattern': r'\b\d{3}-\d{2}-\d{4}\b'
        },
        {
            'rule_type': 'PROFANITY',
            'enabled': True,
            'severity': 'medium',
            'description': 'Detect profanity and offensive language',
            'pattern': r'\b(fuck|shit|damn|bitch|ass|bastard|crap)\b'
        },
        {
            'rule_type': 'VIOLENCE',
            'enabled': True,
            'severity': 'high',
            'description': 'Detect violent content',
            'pattern': r'\b(kill|murder|shoot|stab|attack|harm|hurt|destroy)\b'
        },
        {
            'rule_type': 'FINANCIAL',
            'enabled': True,
            'severity': 'medium',
            'description': 'Detect credit card numbers',
            'pattern': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        },
        {
            'rule_type': 'PROMPT_INJECTION',
            'enabled': True,
            'severity': 'high',
            'description': 'Detect prompt injection attempts',
            'pattern': r'\b(ignore|disregard|forget).*?(previous|above|prior)\s+(instructions|prompt|context)\b'
        }
    ]
    
    @staticmethod
    def initialize_defaults():
        """Initialize default guardrails rules in database"""
        for rule in GuardrailsService.DEFAULT_RULES:
            existing = GuardrailsConfig.query.filter_by(rule_type=rule['rule_type']).first()
            if not existing:
                config = GuardrailsConfig(**rule)
                db.session.add(config)
        
        db.session.commit()
    
    @staticmethod
    def check_content(content, user_id, check_type='both'):
        """
        Check content against guardrails
        
        Args:
            content: Content to check
            user_id: User ID
            check_type: 'input', 'output', or 'both'
            
        Returns:
            dict: Check results with violations and cleaned content
        """
        if not Config.GUARDRAILS_ENABLED:
            return {
                'passed': True,
                'violations': [],
                'cleaned_content': content
            }
        
        # Get enabled rules
        rules = GuardrailsConfig.query.filter_by(enabled=True).all()
        
        violations = []
        cleaned_content = content
        
        for rule in rules:
            if rule.pattern:
                matches = re.finditer(rule.pattern, content, re.IGNORECASE)
                for match in matches:
                    violation = {
                        'rule_type': rule.rule_type,
                        'severity': rule.severity,
                        'matched_text': match.group(),
                        'position': match.span()
                    }
                    violations.append(violation)
                    
                    # Log violation
                    log_entry = GuardrailsLog(
                        user_id=user_id,
                        guardrail_id=rule.id,
                        detected_rule=rule.rule_type,
                        content_snippet=match.group()[:200],
                        action_taken='blocked' if rule.severity == 'high' else 'warned'
                    )
                    db.session.add(log_entry)
                    
                    # Redact high severity violations
                    if rule.severity == 'high':
                        cleaned_content = cleaned_content.replace(
                            match.group(),
                            '[REDACTED]'
                        )
        
        db.session.commit()
        
        # Determine if content passes
        high_severity = [v for v in violations if v['severity'] == 'high']
        passed = len(high_severity) == 0
        
        return {
            'passed': passed,
            'violations': violations,
            'cleaned_content': cleaned_content,
            'action': 'blocked' if not passed else 'allowed'
        }
    
    @staticmethod
    def get_guardrails_config():
        """Get all guardrails configuration"""
        rules = GuardrailsConfig.query.all()
        return [rule.to_dict() for rule in rules]
    
    @staticmethod
    def update_guardrail(rule_id, enabled=None, severity=None, description=None, pattern=None):
        """
        Update guardrail configuration (admin only)
        
        Args:
            rule_id: Rule ID
            enabled: Enable/disable rule
            severity: Rule severity
            description: Rule description
            pattern: Regex pattern
            
        Returns:
            dict: Updated rule
        """
        rule = GuardrailsConfig.query.get(rule_id)
        
        if not rule:
            raise ValueError('Guardrail rule not found')
        
        if enabled is not None:
            rule.enabled = enabled
        
        if severity:
            rule.severity = severity
        
        if description:
            rule.description = description
        
        if pattern:
            # Validate regex pattern
            try:
                re.compile(pattern)
                rule.pattern = pattern
            except re.error:
                raise ValueError('Invalid regex pattern')
        
        db.session.commit()
        
        return rule.to_dict()
    
    @staticmethod
    def create_guardrail(rule_type, enabled=True, severity='medium', description='', pattern=''):
        """
        Create new guardrail rule (admin only)
        
        Args:
            rule_type: Rule type identifier
            enabled: Enable/disable rule
            severity: Rule severity
            description: Rule description
            pattern: Regex pattern
            
        Returns:
            dict: Created rule
        """
        # Check if rule type already exists
        existing = GuardrailsConfig.query.filter_by(rule_type=rule_type).first()
        if existing:
            raise ValueError(f'Rule type {rule_type} already exists')
        
        # Validate pattern if provided
        if pattern:
            try:
                re.compile(pattern)
            except re.error:
                raise ValueError('Invalid regex pattern')
        
        rule = GuardrailsConfig(
            rule_type=rule_type,
            enabled=enabled,
            severity=severity,
            description=description,
            pattern=pattern
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return rule.to_dict()
    
    @staticmethod
    def delete_guardrail(rule_id):
        """Delete guardrail rule (admin only)"""
        rule = GuardrailsConfig.query.get(rule_id)
        
        if not rule:
            raise ValueError('Guardrail rule not found')
        
        db.session.delete(rule)
        db.session.commit()
        
        return {'message': f'Guardrail rule {rule.rule_type} deleted'}
    
    @staticmethod
    def get_guardrails_logs(user_id=None, limit=100):
        """
        Get guardrails detection logs (admin only)
        
        Args:
            user_id: Filter by specific user
            limit: Maximum number of logs
            
        Returns:
            list: Guardrails logs
        """
        query = GuardrailsLog.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        logs = query.order_by(GuardrailsLog.timestamp.desc()).limit(limit).all()
        
        return [log.to_dict() for log in logs]
    
    @staticmethod
    def toggle_guardrails(enabled):
        """
        Toggle all guardrails on/off (admin only)
        
        Args:
            enabled: True to enable, False to disable
            
        Returns:
            dict: Status message
        """
        # This would update the config, but we'll use the Config.GUARDRAILS_ENABLED
        # In a production system, this would update a database setting
        return {
            'enabled': enabled,
            'message': f'Guardrails {"enabled" if enabled else "disabled"}. Note: Update GUARDRAILS_ENABLED in config.'
        }
