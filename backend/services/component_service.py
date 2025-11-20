from models import db, ComponentAccess, Role, ComponentMetadata
from services.auth_service import AuthService

# Available components in the system
AVAILABLE_COMPONENTS = [
    'AGENTIC_RAG',
    'NORMAL_CHAT',
    'GUARDRAILS_INSIGHTS'
]

# Admin-only components (always accessible by admin)
ADMIN_ONLY_COMPONENTS = [
    'USER_MANAGEMENT',
    'COMPONENT_MANAGEMENT',
    'GUARDRAILS_CONFIGURATION',
    'ROLE_MANAGEMENT'
]

class ComponentService:
    """Component/View management service"""
    
    @staticmethod
    def get_available_components():
        """
        Get list of all available components
        
        Returns:
            dict: Assignable and admin-only components
        """
        return {
            'assignable': AVAILABLE_COMPONENTS,
            'admin_only': ADMIN_ONLY_COMPONENTS
        }
    
    @staticmethod
    def get_user_components():
        """
        Get components accessible by current user
        
        Returns:
            list: List of accessible component names
        """
        user = AuthService.get_current_user()
        
        # Admin has access to all components
        if user.is_admin():
            return AVAILABLE_COMPONENTS + ADMIN_ONLY_COMPONENTS
        
        # Get components accessible by any of user's roles
        accessible_components = set()
        for role in user.roles:
            access_records = ComponentAccess.query.filter_by(
                role_id=role.id,
                has_access=True
            ).all()
            accessible_components.update(record.component_name for record in access_records)
        
        return list(accessible_components)
    
    @staticmethod
    def get_role_components(role_name):
        """
        Get components accessible by a specific role
        
        Args:
            role_name: Role name
            
        Returns:
            list: List of accessible component names
        """
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise ValueError(f'Role not found: {role_name}')
        
        # Admin has access to all
        if role.name == 'admin':
            return AVAILABLE_COMPONENTS + ADMIN_ONLY_COMPONENTS
        
        # Get role's assigned components
        access_records = ComponentAccess.query.filter_by(
            role_id=role.id,
            has_access=True
        ).all()
        
        return [record.component_name for record in access_records]
    
    @staticmethod
    def assign_component_to_role(role_name, component_name, has_access=True):
        """
        Assign or remove component access for a role (admin only)
        
        Args:
            role_name: Role name
            component_name: Component name
            has_access: Whether to grant or revoke access
            
        Returns:
            dict: Updated access record
            
        Raises:
            ValueError: If invalid role or component
        """
        # Get role
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise ValueError(f'Role not found: {role_name}')
        
        # Validate component
        if component_name not in AVAILABLE_COMPONENTS:
            raise ValueError(f'Invalid component: {component_name}')
        
        # Find or create access record
        access = ComponentAccess.query.filter_by(
            role_id=role.id,
            component_name=component_name
        ).first()
        
        if access:
            access.has_access = has_access
        else:
            access = ComponentAccess(
                role_id=role.id,
                component_name=component_name,
                has_access=has_access
            )
            db.session.add(access)
        
        db.session.commit()
        
        return access.to_dict()
    
    @staticmethod
    def bulk_assign_components(role_name, component_assignments):
        """
        Bulk assign components to a role
        
        Args:
            role_name: Role name
            component_assignments: Dict of {component_name: has_access}
            
        Returns:
            list: List of updated access records
        """
        results = []
        
        for component_name, has_access in component_assignments.items():
            try:
                result = ComponentService.assign_component_to_role(
                    role_name, component_name, has_access
                )
                results.append(result)
            except ValueError as e:
                results.append({'component_name': component_name, 'error': str(e)})
        
        return results
    
    @staticmethod
    def get_navigation_for_user():
        """
        Get navigation menu items for the current authenticated user.
        Filters components based on user's roles.
        
        Returns:
            list: List of navigation items with metadata
        """
        user = AuthService.get_current_user()
        
        # Get all component metadata  
        components = ComponentMetadata.query.all()
        
        nav_items = []
        for component in components:
            # Check if user has access to this component
            if user.is_admin():
                # Admin sees everything
                has_access = True
                admin_only = component.name in ADMIN_ONLY_COMPONENTS
            else:
                # Check if component is admin-only
                if component.name in ADMIN_ONLY_COMPONENTS:
                    has_access = False
                    admin_only = True
                else:
                    # Check if user has access via their roles
                    has_access = False
                    for role in user.roles:
                        access = ComponentAccess.query.filter_by(
                            role_id=role.id,
                            component_name=component.name,
                            has_access=True
                        ).first()
                        if access:
                            has_access = True
                            break
                    admin_only = False
            
            # Add to navigation if user has access
            if has_access:
                nav_items.append({
                    'name': component.name,
                    'label': component.label,
                    'icon': component.icon,
                    'description': component.description,
                    'admin_only': admin_only
                })
        
        return nav_items
    
    @staticmethod
    def verify_component_access(component_name):
        """
        Verify current user has access to a component
        
        Args:
            component_name: Component name to check
            
        Returns:
            bool: True if user has access
            
        Raises:
            ValueError: If access denied
        """
        user = AuthService.get_current_user()
        
        # Admin has access to all
        if user.is_admin():
            return True
        
        # Check if component is admin-only
        if component_name in ADMIN_ONLY_COMPONENTS:
            raise ValueError('Admin access required')
        
        # Check if component is assignable
        if component_name not in AVAILABLE_COMPONENTS:
            raise ValueError(f'Invalid component: {component_name}')
        
        # Check access records for all user's roles
        for role in user.roles:
            access = ComponentAccess.query.filter_by(
                role_id=role.id,
                component_name=component_name,
                has_access=True
            ).first()
            
        accessible_components = set()
        for role in user.roles:
            access_records = ComponentAccess.query.filter_by(
                role_id=role.id,
                has_access=True
            ).all()
            accessible_components.update(record.component_name for record in access_records)
        
        return list(accessible_components)
    
    @staticmethod
    def get_role_components(role_name):
        """
        Get components accessible by a specific role
        
        Args:
            role_name: Role name
            
        Returns:
            list: List of accessible component names
        """
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise ValueError(f'Role not found: {role_name}')
        
        # Admin has access to all
        if role.name == 'admin':
            return AVAILABLE_COMPONENTS + ADMIN_ONLY_COMPONENTS
        
        # Get role's assigned components
        access_records = ComponentAccess.query.filter_by(
            role_id=role.id,
            has_access=True
        ).all()
        
        return [record.component_name for record in access_records]
    
    @staticmethod
    def assign_component_to_role(role_name, component_name, has_access=True):
        """
        Assign or remove component access for a role (admin only)
        
        Args:
            role_name: Role name
            component_name: Component name
            has_access: Whether to grant or revoke access
            
        Returns:
            dict: Updated access record
            
        Raises:
            ValueError: If invalid role or component
        """
        # Get role
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise ValueError(f'Role not found: {role_name}')
        
        # Validate component
        if component_name not in AVAILABLE_COMPONENTS:
            raise ValueError(f'Invalid component: {component_name}')
        
        # Find or create access record
        access = ComponentAccess.query.filter_by(
            role_id=role.id,
            component_name=component_name
        ).first()
        
        if access:
            access.has_access = has_access
        else:
            access = ComponentAccess(
                role_id=role.id,
                component_name=component_name,
                has_access=has_access
            )
            db.session.add(access)
        
        db.session.commit()
        
        return access.to_dict()
    
    @staticmethod
    def bulk_assign_components(role_name, component_assignments):
        """
        Bulk assign components to a role
        
        Args:
            role_name: Role name
            component_assignments: Dict of {component_name: has_access}
            
        Returns:
            list: List of updated access records
        """
        results = []
        
        for component_name, has_access in component_assignments.items():
            try:
                result = ComponentService.assign_component_to_role(
                    role_name, component_name, has_access
                )
                results.append(result)
            except ValueError as e:
                results.append({'component_name': component_name, 'error': str(e)})
        
        return results
    
    @staticmethod
    def get_navigation_for_user():
        """
        Get navigation menu items for the current authenticated user.
        Filters components based on user's roles.
        
        Returns:
            list: List of navigation items with metadata
        """
        user = AuthService.get_current_user()
        
        # Get all component metadata  
        components = ComponentMetadata.query.all()
        
        nav_items = []
        for component in components:
            # Check if user has access to this component
            if user.is_admin():
                # Admin sees everything
                has_access = True
                admin_only = component.name in ADMIN_ONLY_COMPONENTS
            else:
                # Check if component is admin-only
                if component.name in ADMIN_ONLY_COMPONENTS:
                    has_access = False
                    admin_only = True
                else:
                    # Check if user has access via their roles
                    has_access = False
                    for role in user.roles:
                        access = ComponentAccess.query.filter_by(
                            role_id=role.id,
                            component_name=component.name,
                            has_access=True
                        ).first()
                        if access:
                            has_access = True
                            break
                    admin_only = False
            
            # Add to navigation if user has access
            if has_access:
                nav_items.append({
                    'name': component.name,
                    'label': component.label,
                    'icon': component.icon,
                    'description': component.description,
                    'admin_only': admin_only
                })
        
        return nav_items
    
    @staticmethod
    def verify_component_access(component_name):
        """
        Verify current user has access to a component
        
        Args:
            component_name: Component name to check
            
        Returns:
            bool: True if user has access
            
        Raises:
            ValueError: If access denied
        """
        user = AuthService.get_current_user()
        
        # Admin has access to all
        if user.is_admin():
            return True
        
        # Check if component is admin-only
        if component_name in ADMIN_ONLY_COMPONENTS:
            raise ValueError('Admin access required')
        
        # Check if component is assignable
        if component_name not in AVAILABLE_COMPONENTS:
            raise ValueError(f'Invalid component: {component_name}')
        
        # Check access records for all user's roles
        for role in user.roles:
            access = ComponentAccess.query.filter_by(
                role_id=role.id,
                component_name=component_name,
                has_access=True
            ).first()
            
            if access:
                return True
        
        raise ValueError(f'Access denied to component: {component_name}')
