from django.forms.models import model_to_dict
from api.models import COE, AreaOfResearch, Labs, Project, ProjectMemberPrivilege, ProjectMemberRelationship
import logging

logger = logging.getLogger(__name__)

def create_project(name, abstract, paper_link, head, department, tags, aor, labs, coes):
    """
        Helper to create project and assign project user relationship
    """
    try:
        project_member_privilege = ProjectMemberPrivilege.objects.filter(name = "Admin")
        if head.is_staff:
            project = Project.objects.create(name = name, abstract = abstract, paper_link = paper_link, head = head, department = department, tags = tags)
            aor_set = AreaOfResearch.objects.filter(name__in=aor)
            labs_set = Labs.objects.filter(name__in=labs)
            coes_set = COE.objects.filter(name__in=coes)
            project.aor_tags.add(*aor_set)
            project.labs_tags.add(*labs_set)
            project.coe_tags.add(*coes_set)
            ProjectMemberRelationship.objects.create(project = project, user = head, privilege = project_member_privilege[0])
            return True
        else:
            logger.error("Admin access not found")
            return False
    except Exception as e:
        logger.error(e)
        return False

def get_project_with_id(id):
    try:
        project = Project.objects.get(pk=id)
        project_response = model_to_dict(project,exclude=['aor_tags', 'labs_tags', 'coe_tags'])
        project_response['aor_tags'] = [{**model_to_dict(tag, exclude=['department']), 'department': tag.department.short_name} for tag in project.aor_tags.all()]
        project_response['labs_tags'] = [{**model_to_dict(tag, exclude=['department']), 'department': tag.department.short_name} for tag in project.labs_tags.all()]
        project_response['coe_tags'] = [{**model_to_dict(tag)} for tag in project.coe_tags.all()]
        project_response["department"] = model_to_dict(project.department)
        project_response["head"] = {
            **model_to_dict(project.head, ['name', 'email', 'is_staff']),
            **{'image_url': project.head.image_url }
        }
        
        project_relationships = ProjectMemberRelationship.objects.filter(project=project)
        project_relationships_dict = []
        
        for rel in project_relationships:
            rel_obj = {
            **model_to_dict(rel.user, ['name', 'email', 'is_staff']),
            **{'image_url': rel.user.image_url },
            **{'permission': rel.privilege.name},
            }
            # rel_obj['user'] = model_to_dict(rel.user)
            project_relationships_dict.append(rel_obj)
        
        project_response["members"] = project_relationships_dict
        project_response["success"] = True
        return project_response
    except Exception as e:
        logger.error(e)
        return {'success': False}
    
