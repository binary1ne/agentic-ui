from models import db
from models.component_entities import ComponentModel, ComponentRoleMappingModel
from models.auth_entities import RoleModel
from services.auth_services.auth_service import AuthService

class ComponentService:
    """Component/View management service"""
    
    @staticmethod
    def get_available_components():
        """
        Get list of all available components from database
        
        Returns:
            dict: Components categorized by type (simplified for now)
        """
        # Fetch all active components
        components = ComponentModel.query.filter_by(active_flag=True).all()
        
        # For backward compatibility, we'll categorize them
        # Ideally, we should have a 'type' or 'category' field in ComponentModel
        # For now, we'll just return all as assignable
        component_names = [c.template_name for c in components]
        
        return {
            'assignable': component_names,
            'admin_only': [] # Deprecated concept, controlled by roles now
        }
    
    @staticmethod
    def get_user_components():
        """
        Get components accessible by current user
        
        Returns:
            list: List of accessible component names
        """
        user = AuthService.get_current_user()
        
        # Get components accessible by any of user's roles
        accessible_components = set()
        
        for user_role in user.user_roles:
            if not user_role.active_flag:
                continue
                
            role = user_role.role
            # Get component mappings for this role
            mappings = ComponentRoleMappingModel.query.filter_by(
                role_id=role.role_id,
                active_flag=True
            ).all()
            
            for mapping in mappings:
                if mapping.template and mapping.template.active_flag:
                    accessible_components.add(mapping.template.template_name)
        
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
        role = RoleModel.query.filter_by(role_name=role_name).first()
        if not role:
            raise ValueError(f'Role not found: {role_name}')
        
        # Get role's assigned components
        mappings = ComponentRoleMappingModel.query.filter_by(
            role_id=role.role_id,
            active_flag=True
        ).all()
        
        components = []
        for mapping in mappings:
            if mapping.template and mapping.template.active_flag:
                components.append(mapping.template.template_name)
                
        return components
    
    @staticmethod
    def assign_component_to_role(role_name, component_name, has_access=True):
        """
        Assign or remove component access for a role (admin only)
        
        Args:
            role_name: Role name
            component_name: Component name (template_name)
            has_access: Whether to grant or revoke access (sets active_flag)
            
        Returns:
            dict: Updated access record
        """
        # Get role
        role = RoleModel.query.filter_by(role_name=role_name).first()
        if not role:
            raise ValueError(f'Role not found: {role_name}')
        
        # Find template
        template = ComponentModel.query.filter_by(template_name=component_name).first()
        if not template:
            # Dynamic creation if not exists? 
            # For now, assume it must exist. If we want dynamic creation, we need more info (mode, value)
            raise ValueError(f'Component template not found: {component_name}')
        
        # Find or create access record
        mapping = ComponentRoleMappingModel.query.filter_by(
            role_id=role.role_id,
            template_id=template.template_id
        ).first()
        
        if mapping:
            mapping.active_flag = has_access
        else:
            mapping = ComponentRoleMappingModel(
                role_id=role.role_id,
                template_id=template.template_id,
                active_flag=has_access
            )
            db.session.add(mapping)
        
        db.session.commit()
        
        return mapping.to_dict()
    
    @staticmethod
    def bulk_assign_components(role_name, component_assignments):
        """
        Bulk assign components to a role
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
    def get_navigation(active_role:str):
        try:
            """
            Return navigation items for the ACTIVE ROLE (from JWT).
            Uses efficient JOINs instead of multiple DB queries.
            """

            # Fetch the role record
            role = RoleModel.query.filter_by(role_name=active_role, active_flag=True).first()
            if not role:
                return []

            # Single JOIN query: roles -> template_role_mapping -> templates
            results = (
                db.session.query(ComponentModel)
                .join(ComponentRoleMappingModel, ComponentRoleMappingModel.template_id == ComponentModel.template_id)
                .filter(
                    ComponentRoleMappingModel.role_id == role.role_id,
                    ComponentRoleMappingModel.active_flag == True,
                    ComponentModel.active_flag == True
                )
                .all()
            )

            # Convert results to navigation structure
            nav_items = []
            for template in results:
                nav_items.append({
                    'name': template.template_name,
                    'label': template.template_name,
                    'icon': template.template_icon or '🔐', 
                    'description': template.description,
                    'admin_only': False,
                    'mode': template.component_mode,
                    'value': template.component_value
                })

            return nav_items

        except Exception as e:
            import traceback
            print(f"Navigation error: {str(e)}")
            print(traceback.format_exc())
            return []

    @staticmethod
    def get_navigation_for_user():
        """
        Get navigation menu items for the current authenticated user.
        Filters components based on user's roles.
        
        Returns:
            list: List of navigation items with metadata
        """
        user = AuthService.get_current_user()
        
        # Get all active templates
        templates = ComponentModel.query.filter_by(active_flag=True).all()
        
        nav_items = []
        for template in templates:
            # Check access
            has_access = False
            
            # Check if user has access via their roles
            for user_role in user.user_roles:
                if not user_role.active_flag:
                    continue
                
                mapping = ComponentRoleMappingModel.query.filter_by(
                    role_id=user_role.role_id,
                    template_id=template.template_id,
                    active_flag=True
                ).first()
                
                if mapping:
                    has_access = True
                    break
            
            # Add to navigation if user has access
            if has_access:
                nav_items.append({
                    'name': template.template_name,
                    'label': template.template_name, 
                    'icon': 'extension', # Default icon, could be stored in DB if we add a column
                    'description': template.description,
                    'admin_only': False, # Deprecated concept
                    'mode': template.component_mode,
                    'value': template.component_value
                })
        
        return nav_items
    
    @staticmethod
    def verify_component_access(component_name):
        """
        Verify current user has access to a component
        """
        user = AuthService.get_current_user()
        
        # Find template
        template = ComponentModel.query.filter_by(template_name=component_name).first()
        if not template or not template.active_flag:
             raise ValueError(f'Component not found or inactive: {component_name}')

        # Check access records for all user's roles
        for user_role in user.user_roles:
            if not user_role.active_flag:
                continue
                
            mapping = ComponentRoleMappingModel.query.filter_by(
                role_id=user_role.role_id,
                template_id=template.template_id,
                active_flag=True
            ).first()
            
            if mapping:
                return True
        
        raise ValueError(f'Access denied to component: {component_name}')
